import pytest
from uuid import uuid4
from datetime import datetime, timezone
from httpx import AsyncClient
from app.modules.users.models import User, UserRole
from app.modules.rate_customizations.models import RateCustomization
from app.modules.rate_categories.models import RateCategory
from app.modules.trips.models import Trip, TripStatus
from app.modules.expenses.models import Expense
from tests.modules.auth.test_helpers import register, login


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserWorkflowIntegration:
    """Integration tests for the complete user workflow with authentication"""

    async def test_complete_user_workflow(self, client: AsyncClient, test_db_session):
        """Test the complete workflow: register -> create customization -> create category -> start trip -> add expenses -> end trip"""
        
        # 1. Register and login user
        await register(client, email="testuser@example.com", password="TestPass123!")
        login_response = await login(client, email="testuser@example.com", password="TestPass123!")
        assert login_response.status_code == 200
        
        auth_data = login_response.json()
        access_token = auth_data["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Create a rate customization
        customization_data = {
            "name": "2024 Business Rates",
            "description": "Standard business mileage rates for 2024",
            "year": 2024
        }
        
        customization_response = await client.post(
            "/api/v1/rate-customizations/",
            json=customization_data,
            headers=headers
        )
        assert customization_response.status_code == 200
        customization = customization_response.json()
        customization_id = customization["id"]
        
        # 3. Create a rate category
        category_data = {
            "name": "Business Mileage",
            "cost_per_mile": 0.67
        }
        
        category_response = await client.post(
            f"/api/v1/rate-customizations/{customization_id}/categories/",
            json=category_data,
            headers=headers
        )
        assert category_response.status_code == 200
        category = category_response.json()
        category_id = category["id"]
        
        # 4. Start a trip
        trip_data = {
            "start_address": "123 Main St, Anytown, USA",
            "purpose": "Client meeting",
            "vehicle": "Company Car",
            "rate_customization_id": customization_id,
            "rate_category_id": category_id
        }
        
        trip_response = await client.post(
            "/api/v1/trips/",
            json=trip_data,
            headers=headers
        )
        assert trip_response.status_code == 200
        trip = trip_response.json()
        trip_id = trip["id"]
        assert trip["status"] == "active"
        
        # 5. Add expenses to the trip
        expense_data = {
            "type": "Parking",
            "amount": 15.50
        }
        
        expense_response = await client.post(
            f"/api/v1/trips/{trip_id}/expenses/",
            json=expense_data,
            headers=headers
        )
        assert expense_response.status_code == 200
        expense = expense_response.json()
        assert expense["amount"] == 15.50
        
        # 6. Get trip expenses
        expenses_response = await client.get(
            f"/api/v1/trips/{trip_id}/expenses/",
            headers=headers
        )
        assert expenses_response.status_code == 200
        expenses = expenses_response.json()
        assert len(expenses) == 1
        assert expenses[0]["type"] == "Parking"
        
        # 7. End the trip
        end_trip_data = {
            "end_address": "456 Oak Ave, Anytown, USA",
            "geometry": {"type":"LineString","coordinates":[[-122.4194,37.7749],[-122.4094,37.7849]]},
            "distance_meters": 41040.0  # 25.5 miles in meters
        }
        
        end_trip_response = await client.patch(
            f"/api/v1/trips/{trip_id}/end",
            json=end_trip_data,
            headers=headers
        )
        assert end_trip_response.status_code == 200
        completed_trip = end_trip_response.json()
        assert completed_trip["status"] == "completed"
        assert completed_trip["miles"] == 25.5
        
        # 8. Verify trip totals
        final_trip_response = await client.get(
            f"/api/v1/trips/{trip_id}",
            headers=headers
        )
        assert final_trip_response.status_code == 200
        final_trip = final_trip_response.json()
        
        # Verify mileage reimbursement (25.5 miles * $0.67)
        expected_mileage = 25.5 * 0.67
        assert abs(final_trip["mileage_reimbursement_total"] - expected_mileage) < 0.01
        
        # Verify expense reimbursement
        assert final_trip["expense_reimbursement_total"] == 15.50
        
        # Verify total reimbursement
        expected_total = expected_mileage + 15.50
        assert abs(final_trip["total_reimbursement"] - expected_total) < 0.01

    async def test_user_isolation(self, client: AsyncClient, test_db_session):
        """Test that users can only access their own data"""
        
        # Register two users
        await register(client, email="user1@example.com", password="TestPass123!")
        await register(client, email="user2@example.com", password="TestPass123!")
        
        # Login user1
        user1_login = await login(client, email="user1@example.com", password="TestPass123!")
        user1_data = user1_login.json()
        user1_headers = {"Authorization": f"Bearer {user1_data['tokens']['access_token']}"}
        
        # Login user2  
        user2_login = await login(client, email="user2@example.com", password="TestPass123!")
        user2_data = user2_login.json()
        user2_headers = {"Authorization": f"Bearer {user2_data['tokens']['access_token']}"}
        
        # User1 creates a customization
        customization_data = {
            "name": "User1 Rates",
            "description": "User1's rates",
            "year": 2024
        }
        
        user1_customization = await client.post(
            "/api/v1/rate-customizations/",
            json=customization_data,
            headers=user1_headers
        )
        assert user1_customization.status_code == 200
        customization_id = user1_customization.json()["id"]
        
        # User2 tries to access User1's customization - should fail
        user2_access = await client.get(
            f"/api/v1/rate-customizations/{customization_id}",
            headers=user2_headers
        )
        assert user2_access.status_code == 404  # Not found (user doesn't own it)
        
        # User1 can access their own customization
        user1_access = await client.get(
            f"/api/v1/rate-customizations/{customization_id}",
            headers=user1_headers
        )
        assert user1_access.status_code == 200
        
        # User2 creates their own customization with the same name (should work due to user isolation)
        user2_customization = await client.post(
            "/api/v1/rate-customizations/",
            json=customization_data,  # Same data
            headers=user2_headers
        )
        assert user2_customization.status_code == 200
        user2_customization_id = user2_customization.json()["id"]
        
        # Both users can list their own customizations
        user1_list = await client.get("/api/v1/rate-customizations/", headers=user1_headers)
        user2_list = await client.get("/api/v1/rate-customizations/", headers=user2_headers)
        
        assert user1_list.status_code == 200
        assert user2_list.status_code == 200
        
        user1_customizations = user1_list.json()
        user2_customizations = user2_list.json()
        
        # Each user should only see their own customization
        assert len(user1_customizations) == 1
        assert len(user2_customizations) == 1
        assert user1_customizations[0]["id"] != user2_customizations[0]["id"]

    async def test_trip_ownership_validation(self, client: AsyncClient, test_db_session):
        """Test that users can only access their own trips"""
        
        # Setup two users with trips
        await register(client, email="tripuser1@example.com", password="TestPass123!")
        await register(client, email="tripuser2@example.com", password="TestPass123!")
        
        user1_login = await login(client, email="tripuser1@example.com", password="TestPass123!")
        user1_headers = {"Authorization": f"Bearer {user1_login.json()['tokens']['access_token']}"}
        
        user2_login = await login(client, email="tripuser2@example.com", password="TestPass123!")
        user2_headers = {"Authorization": f"Bearer {user2_login.json()['tokens']['access_token']}"}
        
        # Create minimal setup for user1
        customization_response = await client.post(
            "/api/v1/rate-customizations/",
            json={"name": "Test Rates", "year": 2024},
            headers=user1_headers
        )
        customization_id = customization_response.json()["id"]
        
        category_response = await client.post(
            f"/api/v1/rate-customizations/{customization_id}/categories/",
            json={"name": "Business", "cost_per_mile": 0.67},
            headers=user1_headers
        )
        category_id = category_response.json()["id"]
        
        # User1 creates a trip
        trip_data = {
            "start_address": "123 Test St",
            "purpose": "Business meeting",
            "rate_customization_id": customization_id,
            "rate_category_id": category_id
        }
        
        trip_response = await client.post("/api/v1/trips/", json=trip_data, headers=user1_headers)
        assert trip_response.status_code == 200
        trip_id = trip_response.json()["id"]
        
        # User2 tries to access User1's trip - should fail
        user2_trip_access = await client.get(f"/api/v1/trips/{trip_id}", headers=user2_headers)
        assert user2_trip_access.status_code == 404
        
        # User1 can access their own trip
        user1_trip_access = await client.get(f"/api/v1/trips/{trip_id}", headers=user1_headers)
        assert user1_trip_access.status_code == 200
        
        # User2 tries to add expenses to User1's trip - should fail
        expense_data = {"type": "Parking", "amount": 10.0}
        user2_expense = await client.post(
            f"/api/v1/trips/{trip_id}/expenses/",
            json=expense_data,
            headers=user2_headers
        )
        assert user2_expense.status_code == 404  # Trip not found for user2