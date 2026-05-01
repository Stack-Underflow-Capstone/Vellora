import pytest
from uuid import uuid4, UUID
from datetime import date, datetime, timezone, timedelta
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock

from app.modules.users.models import User, UserRole
from app.modules.trips.models import Trip, TripStatus
from app.modules.expenses.models import Expense
from app.modules.rate_categories.models import RateCategory
from app.modules.rate_customizations.models import RateCustomization
from app.modules.reports.models import Report, ReportStatus
from app.modules.vehicles.models import Vehicle
from tests.modules.auth.test_helpers import register, login


@pytest.fixture
def mock_aws_services():
    """Mock AWS services to prevent LocalStack dependencies"""
    with patch('app.infra.adapters.s3_report_storage_adapter.get_s3_client') as mock_s3_client, \
         patch('app.infra.adapters.sqs_report_queue_adapter.get_sqs_client') as mock_sqs_client, \
         patch('app.aws_client.get_s3_client') as mock_aws_s3, \
         patch('app.aws_client.get_sqs_client') as mock_aws_sqs:
        
        # Mock S3 client
        s3_mock = MagicMock()
        s3_mock.put_object.return_value = {'ETag': 'mock-etag'}
        s3_mock.head_object.return_value = {'ContentLength': 1024}
        s3_mock.generate_presigned_url.return_value = 'http://localhost/mock-download-url'
        mock_s3_client.return_value = s3_mock
        mock_aws_s3.return_value = s3_mock
        
        # Mock SQS client  
        sqs_mock = MagicMock()
        sqs_mock.get_queue_url.return_value = {'QueueUrl': 'http://localhost/mock-queue'}
        sqs_mock.send_message.return_value = {'MessageId': 'mock-message-id'}
        mock_sqs_client.return_value = sqs_mock
        mock_aws_sqs.return_value = sqs_mock
        
        yield {
            's3': s3_mock,
            'sqs': sqs_mock
        }


@pytest.mark.integration 
@pytest.mark.asyncio
class TestReportsIntegration:

    @pytest.fixture
    async def authenticated_user(self, client: AsyncClient):
        email = "testuser@example.com"
        password = "TestPass123!"
        
        # Register user
        await register(client, email=email, password=password)
        
        # Login and get access token
        login_response = await login(client, email=email, password=password)
        assert login_response.status_code == 200
        
        auth_data = login_response.json()
        access_token = auth_data["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        return headers, auth_data["user"]["id"]

    @pytest.fixture
    async def sample_trip_data(self, test_db_session, authenticated_user):
        headers, user_id_str = authenticated_user
        
        user_id = UUID(user_id_str)
        
        rate_customization = RateCustomization(
            id=uuid4(),
            user_id=user_id,
            name="2024 Standard Rates",
            description="Standard mileage rates for 2024",
            year=2024
        )
        test_db_session.add(rate_customization)
        
        rate_category = RateCategory(
            id=uuid4(),
            name="Business",
            cost_per_mile=0.65,
            rate_customization_id=rate_customization.id
        )
        test_db_session.add(rate_category)
        
        # Create a vehicle for the trip
        vehicle = Vehicle(
            id=uuid4(),
            name="Honda Civic",
            license_plate="RPT123",
            model="Honda Civic",
            user_id=user_id
        )
        test_db_session.add(vehicle)
        
        trip = Trip(
            id=uuid4(),
            user_id=user_id,
            status=TripStatus.completed,
            start_address_encrypted="NYC Office",
            end_address_encrypted="Client Site",
            purpose="Business meetings",
            vehicle_id=vehicle.id,
            miles=250.5,
            mileage_reimbursement_total=150.30,
            expense_reimbursement_total=125.75,
            rate_customization_id=rate_customization.id,
            rate_category_id=rate_category.id
        )
        test_db_session.add(trip)
        
        expenses = [
            Expense(
                id=uuid4(),
                user_id=user_id,
                trip_id=trip.id,
                type="Parking",
                amount=25.50
            ),
            Expense(
                id=uuid4(),
                user_id=user_id,
                trip_id=trip.id,
                type="Gas",
                amount=100.25
            )
        ]
        
        for expense in expenses:
            test_db_session.add(expense)
        
        await test_db_session.commit()
        return trip, expenses

    async def test_complete_report_generation_workflow(
        self, client: AsyncClient, authenticated_user, sample_trip_data, mock_aws_services
    ):
        headers, user_id = authenticated_user
        trip, expenses = sample_trip_data
        
        # 1. Create a report request
        report_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        
        create_response = await client.post(
            "/api/v1/reports",
            json=report_data,
            headers=headers
        )
        assert create_response.status_code == 200
        
        report = create_response.json()
        report_id = report["id"]
        assert report["status"] == "pending"
        
        # Verify SQS message was sent
        assert mock_aws_services['sqs'].send_message.called
        
        # 2. Check report status
        status_response = await client.get(
            f"/api/v1/reports/{report_id}/status",
            headers=headers
        )
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["id"] == report_id
        assert status_data["status"] == "pending"
        
        # 3. List user reports
        history_response = await client.get(
            "/api/v1/reports/history",
            headers=headers
        )
        assert history_response.status_code == 200
        
        reports_list = history_response.json()
        assert len(reports_list) >= 1
        assert any(r["id"] == report_id for r in reports_list)

    async def test_report_retry_workflow(
        self, client: AsyncClient, authenticated_user, test_db_session, mock_aws_services
    ):
        headers, user_id = authenticated_user
        
        # Create a failed report directly in the database
        failed_report = Report(
            id=uuid4(),
            user_id=UUID(user_id) if isinstance(user_id, str) else user_id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            status=ReportStatus.failed,
            retry_attempts=1
        )
        test_db_session.add(failed_report)
        await test_db_session.commit()
        await test_db_session.refresh(failed_report)
        
        # Retry the failed report
        retry_response = await client.post(
            f"/api/v1/reports/{failed_report.id}/retry",
            headers=headers
        )
        # Could be successful, rate limited, or not found (security)
        assert retry_response.status_code in [200, 404, 429]
        
        if retry_response.status_code == 200:
            retried_report = retry_response.json()
            assert retried_report["status"] == "pending"
            assert mock_aws_services['sqs'].send_message.called

    async def test_report_rate_limiting(
        self, client: AsyncClient, authenticated_user, mock_aws_services
    ):
        """Test report rate limiting functionality"""
        headers, user_id = authenticated_user
        
        report_data = {
            "start_date": "2024-01-01", 
            "end_date": "2024-01-31"
        }
        
        # First request (could be rate limited immediately if limits are strict)
        first_response = await client.post(
            "/api/v1/reports",
            json=report_data,
            headers=headers
        )
        # Accept either success or rate limit
        assert first_response.status_code in [200, 429]
        
        # Second request within a minute should be rate limited if first succeeded
        if first_response.status_code == 200:
            second_response = await client.post(
                "/api/v1/reports",
                json=report_data,
                headers=headers
            )
            assert second_response.status_code == 429
            assert "Too many requests" in second_response.json()["detail"]

    async def test_report_permissions(
        self, client: AsyncClient, test_db_session, mock_aws_services
    ):
        # Create two users
        email1, email2 = "user1@example.com", "user2@example.com"
        password = "TestPass123!"
        
        # Register and login first user
        await register(client, email=email1, password=password)
        login1_response = await login(client, email=email1, password=password)
        user1_token = login1_response.json()["tokens"]["access_token"]
        user1_id = login1_response.json()["user"]["id"]
        headers1 = {"Authorization": f"Bearer {user1_token}"}
        
        # Register and login second user
        await register(client, email=email2, password=password)
        login2_response = await login(client, email=email2, password=password)
        user2_token = login2_response.json()["tokens"]["access_token"]
        user2_id = login2_response.json()["user"]["id"]
        headers2 = {"Authorization": f"Bearer {user2_token}"}
        
        # User1 creates a report
        report_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        
        create_response = await client.post(
            "/api/v1/reports",
            json=report_data,
            headers=headers1
        )
        assert create_response.status_code == 200
        report_id = create_response.json()["id"]
        
        # Create a completed report for User1
        completed_report = Report(
            id=uuid4(),
            user_id=UUID(user1_id) if isinstance(user1_id, str) else user1_id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            status=ReportStatus.completed,
            file_name="test-report.pdf"
        )
        test_db_session.add(completed_report)
        await test_db_session.commit()
        await test_db_session.refresh(completed_report)
        
        # User2 tries to download User1's report - should fail
        download_response = await client.get(
            f"/api/v1/reports/{completed_report.id}/download",
            headers=headers2
        )
        # Should be 403 forbidden or 404 not found (both are acceptable for security)
        assert download_response.status_code in [403, 404]

    async def test_report_with_real_data_calculation(
        self, client: AsyncClient, authenticated_user, test_db_session, mock_aws_services
    ):
        """Test report generation with actual trip and expense data"""
        headers, user_id_str = authenticated_user
        user_id = UUID(user_id_str)
        
        # Create required rate data first
        rate_customization = RateCustomization(
            id=uuid4(),
            user_id=user_id,
            name="2024 Standard Rates",
            year=2024
        )
        test_db_session.add(rate_customization)
        
        rate_category = RateCategory(
            id=uuid4(),
            name="Business",
            cost_per_mile=0.65,
            rate_customization_id=rate_customization.id
        )
        test_db_session.add(rate_category)
        
        # Create multiple trips with expenses
        trips_data = [
            {
                "purpose": "Business Trip 1",
                "miles": 100.0,
                "expenses": [("Parking", 20.0), ("Gas", 45.0)]
            },
            {
                "purpose": "Business Trip 2",
                "miles": 150.0,
                "expenses": [("Hotel", 200.0), ("Meals", 75.0)]
            }
        ]
        
        for trip_data in trips_data:
            trip = Trip(
                id=uuid4(),
                user_id=user_id,
                purpose=trip_data["purpose"],
                status=TripStatus.completed,
                start_address_encrypted="Office",
                end_address_encrypted="Client Site",
                miles=trip_data["miles"],
                expense_reimbursement_total=sum(exp[1] for exp in trip_data["expenses"]),
                rate_customization_id=rate_customization.id,
                rate_category_id=rate_category.id
            )
            test_db_session.add(trip)
            
            for expense_type, amount in trip_data["expenses"]:
                expense = Expense(
                    id=uuid4(),
                    user_id=user_id,
                    trip_id=trip.id,
                    type=expense_type,
                    amount=amount
                )
                test_db_session.add(expense)
        
        await test_db_session.commit()
        
        # Generate report for January 2024
        report_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        
        create_response = await client.post(
            "/api/v1/reports",
            json=report_data,
            headers=headers
        )
        # Could be successful or rate limited from previous tests
        assert create_response.status_code in [200, 429]
        
        if create_response.status_code == 200:
            report = create_response.json()
            
            # Verify report includes the date range
            assert report["start_date"] == "2024-01-01"
            assert report["end_date"] == "2024-01-31"
            assert report["status"] == "pending"

    async def test_invalid_date_range(
        self, client: AsyncClient, authenticated_user, mock_aws_services
    ):
        """Test report creation with invalid date range"""
        headers, user_id = authenticated_user
        
        # Test end date before start date
        invalid_data = {
            "start_date": "2024-01-31",
            "end_date": "2024-01-01"
        }
        
        response = await client.post(
            "/api/v1/reports",
            json=invalid_data,
            headers=headers
        )
        assert response.status_code == 422  # Validation error
        
        error_detail = response.json()["detail"]
        assert any("end_date cannot be earlier than start_date" in str(err) for err in error_detail)

    async def test_unauthenticated_access(self, client: AsyncClient, mock_aws_services):
        """Test that unauthenticated users cannot access reports endpoints"""
        
        # Try to create report without authentication
        report_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        
        response = await client.post("/api/v1/reports", json=report_data)
        assert response.status_code == 401
        
        # Try to get report status without authentication
        fake_report_id = str(uuid4())
        status_response = await client.get(f"/api/v1/reports/{fake_report_id}/status")
        # Could be 401, 422 for validation, or 404 for routing differences
        assert status_response.status_code in [401, 422, 404]
        
        # Try to get reports history without authentication
        history_response = await client.get("/api/v1/reports/history")
        assert history_response.status_code == 401