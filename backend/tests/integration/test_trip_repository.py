
import pytest
from uuid import uuid4
from app.modules.expenses.models import Expense
from app.modules.rate_categories.models import RateCategory
from app.modules.rate_customizations.models import RateCustomization
from app.modules.trips.models import Trip, TripStatus
from app.modules.trips.repository import TripRepo
from app.modules.users.models import User, UserRole
from app.modules.vehicles.models import Vehicle


@pytest.mark.integration
@pytest.mark.asyncio
class TestTripRepoIntegration:

    @pytest.fixture
    async def test_user(self, test_db_session):
        """Create a test user"""
        user = User(
            id=uuid4(),
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed_password",
            role=UserRole.EMPLOYEE
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)
        return user

    async def test_save_trip_with_relationships(self, test_db_session, test_user):
        """Test saving a trip with all required relationships including user"""
        customization = RateCustomization(
            id=uuid4(),
            name="Standard Rate",
            description="Standard mileage rate",
            year=2024,
            user_id=test_user.id
        )
        test_db_session.add(customization)
        await test_db_session.commit()
        
        category = RateCategory(
            id=uuid4(),
            name="Mileage",
            cost_per_mile=0.67,
            rate_customization_id=customization.id
        )
        test_db_session.add(category)
        await test_db_session.commit()
        
        # Create a vehicle for the trip
        vehicle = Vehicle(
            id=uuid4(),
            name="Company Car",
            license_plate="ABC123",
            model="Toyota Camry",
            user_id=test_user.id
        )
        test_db_session.add(vehicle)
        await test_db_session.commit()
        
        trip = Trip(
            id=uuid4(),
            status=TripStatus.active,
            start_address_encrypted="encrypted_start_address",
            purpose="Business meeting",
            vehicle_id=vehicle.id,
            geometry_encrypted="gAAAAABhZ6_encrypted_geometry_data_here",
            rate_customization_id=customization.id,
            rate_category_id=category.id,
            reimbursement_rate=0.67,
            user_id=test_user.id
        )
        
        repo = TripRepo(test_db_session)
        
        result = await repo.save(trip)
        
        assert result.id == trip.id
        assert result.status == TripStatus.active
        assert result.start_address_encrypted == "encrypted_start_address"
        assert result.purpose == "Business meeting"
        assert result.user_id == test_user.id
        
        assert result.rate_customization is not None
        assert result.rate_customization.name == "Standard Rate"
        assert result.rate_category is not None
        assert result.rate_category.name == "Mileage"
        assert len(result.expenses) == 0 

    async def test_get_trip_by_id_with_user_filtering(self, test_db_session, test_user):
        """Test retrieving trip by ID with user filtering"""
        # Create another user to test isolation
        other_user = User(
            id=uuid4(),
            email="other@example.com",
            full_name="Other User",
            password_hash="hashed_password",
            role=UserRole.EMPLOYEE
        )
        test_db_session.add(other_user)
        await test_db_session.commit()
        
        customization = RateCustomization(
            id=uuid4(),
            name="International Rate",
            description="International travel rate",
            year=2024,
            user_id=test_user.id
        )
        test_db_session.add(customization)
        await test_db_session.commit()
        
        category = RateCategory(
            id=uuid4(),
            name="Per Diem",
            cost_per_mile=1.25,
            rate_customization_id=customization.id
        )
        test_db_session.add(category)
        await test_db_session.commit()
        
        # Create a vehicle for the trip
        vehicle = Vehicle(
            id=uuid4(),
            name="Rental Car",
            license_plate="RNT456",
            model="Honda Civic",
            user_id=test_user.id
        )
        test_db_session.add(vehicle)
        await test_db_session.commit()
        
        trip = Trip(
            id=uuid4(),
            status=TripStatus.completed,
            start_address_encrypted="encrypted_start",
            end_address_encrypted="encrypted_end",
            purpose="Client visit",
            vehicle_id=vehicle.id,
            miles=50.5,
            geometry_encrypted="gAAAAABhZ7_client_visit_geometry_encrypted",
            reimbursement_rate=0.67,
            mileage_reimbursement_total=33.84,
            rate_customization_id=customization.id,
            rate_category_id=category.id,
            user_id=test_user.id
        )
        test_db_session.add(trip)
        await test_db_session.commit()
        
        repo = TripRepo(test_db_session)
        
        # Test user can get their own trip
        result = await repo.get(trip.id, user_id=test_user.id)
        assert result is not None
        assert result.id == trip.id
        assert result.status == TripStatus.completed
        assert result.miles == 50.5
        assert result.mileage_reimbursement_total == 33.84
        assert result.user_id == test_user.id
        
        # Other user cannot get the trip
        other_result = await repo.get(trip.id, user_id=other_user.id)
        assert other_result is None
        
        assert result.rate_customization.name == "International Rate"
        assert result.rate_category.name == "Per Diem"

    async def test_get_trip_not_found(self, test_db_session, test_user):
        """Test getting non-existent trip returns None"""
        repo = TripRepo(test_db_session)
        non_existent_id = uuid4()
        
        result = await repo.get(non_existent_id, user_id=test_user.id)
        
        assert result is None

    async def test_save_and_retrieve_trip_with_expenses(self, test_db_session, test_user):
        customization = RateCustomization(
            id=uuid4(), 
            name="Default", 
            year=2024,
            user_id=test_user.id
        )
        test_db_session.add(customization)
        await test_db_session.commit()
        
        category = RateCategory(
            id=uuid4(), 
            name="Travel", 
            cost_per_mile=0.67,
            rate_customization_id=customization.id
        )
        test_db_session.add(category)
        await test_db_session.commit()
        
        # Create a vehicle for the trip
        vehicle = Vehicle(
            id=uuid4(),
            name="Personal Vehicle",
            license_plate="PER789",
            model="Toyota Prius",
            user_id=test_user.id
        )
        test_db_session.add(vehicle)
        await test_db_session.commit()
        
        trip = Trip(
            id=uuid4(),
            status=TripStatus.active,
            start_address_encrypted="encrypted_start",
            vehicle_id=vehicle.id,
            geometry_encrypted="gAAAAABhZ8_travel_geometry_encrypted",
            rate_customization_id=customization.id,
            rate_category_id=category.id,
            reimbursement_rate=0.67,
            user_id=test_user.id
        )
        test_db_session.add(trip)
        await test_db_session.commit()
        
        expense = Expense(
            id=uuid4(),
            trip_id=trip.id,
            type="Hotel",
            amount=150.00,
            user_id=test_user.id
        )
        test_db_session.add(expense)
        await test_db_session.commit()
        
        repo = TripRepo(test_db_session)
        
        result = await repo.get(trip.id, user_id=test_user.id)
        
        assert result is not None
        assert result.user_id == test_user.id
        assert len(result.expenses) == 1
        assert result.expenses[0].type == "Hotel"
        assert result.expenses[0].amount == 150.00
        assert result.expenses[0].user_id == test_user.id

    async def test_save_updates_existing_trip(self, test_db_session, test_user):
        customization = RateCustomization(
            id=uuid4(), 
            name="Standard", 
            year=2024,
            user_id=test_user.id
        )
        test_db_session.add(customization)
        await test_db_session.commit()
        
        category = RateCategory(
            id=uuid4(), 
            name="Mileage", 
            cost_per_mile=0.67,
            rate_customization_id=customization.id
        )
        test_db_session.add(category)
        await test_db_session.commit()
        
        # Create a vehicle for the trip
        vehicle = Vehicle(
            id=uuid4(),
            name="Work Truck",
            license_plate="WRK012",
            model="Ford F-150",
            user_id=test_user.id
        )
        test_db_session.add(vehicle)
        await test_db_session.commit()
        
        trip = Trip(
            id=uuid4(),
            status=TripStatus.active,
            start_address_encrypted="encrypted_start",
            vehicle_id=vehicle.id,
            geometry_encrypted="gAAAAABhZ9_mileage_geometry_encrypted",
            rate_customization_id=customization.id,
            rate_category_id=category.id,
            reimbursement_rate=0.67,
            user_id=test_user.id
        )
        test_db_session.add(trip)
        await test_db_session.commit()
        
        repo = TripRepo(test_db_session)
        
        trip.purpose = "Updated purpose"
        trip.status = TripStatus.completed
        trip.miles = 100.0
        trip.mileage_reimbursement_total = 67.0
        
        updated_trip = await repo.save(trip)
        
        assert updated_trip.purpose == "Updated purpose"
        assert updated_trip.status == TripStatus.completed
        assert updated_trip.miles == 100.0
        assert updated_trip.mileage_reimbursement_total == 67.0
        assert updated_trip.user_id == test_user.id  # User ownership preserved
        
        retrieved = await repo.get(trip.id, user_id=test_user.id)
        assert retrieved.purpose == "Updated purpose"
        assert retrieved.status == TripStatus.completed
        assert retrieved.user_id == test_user.id

    async def test_list_trips_filtered_by_user(self, test_db_session, test_user):
        # Create another user with their own trip
        other_user = User(
            id=uuid4(),
            email="other2@example.com", 
            full_name="Other User 2",
            password_hash="hashed_password",
            role=UserRole.EMPLOYEE
        )
        test_db_session.add(other_user)
        await test_db_session.commit()
        
        # Create customizations for both users
        user_customization = RateCustomization(
            id=uuid4(), 
            name="User Customization", 
            year=2024,
            user_id=test_user.id
        )
        other_customization = RateCustomization(
            id=uuid4(), 
            name="Other Customization", 
            year=2024,
            user_id=other_user.id
        )
        test_db_session.add_all([user_customization, other_customization])
        await test_db_session.commit()
        
        # Create categories
        user_category = RateCategory(
            id=uuid4(), 
            name="User Category", 
            cost_per_mile=0.67,
            rate_customization_id=user_customization.id
        )
        other_category = RateCategory(
            id=uuid4(), 
            name="Other Category", 
            cost_per_mile=0.67,
            rate_customization_id=other_customization.id
        )
        test_db_session.add_all([user_category, other_category])
        await test_db_session.commit()
        
        # Create trips for both users
        user_trip = Trip(
            id=uuid4(),
            status=TripStatus.active,
            start_address_encrypted="user_trip_start",
            purpose="User business meeting",
            rate_customization_id=user_customization.id,
            rate_category_id=user_category.id,
            reimbursement_rate=0.67,
            user_id=test_user.id
        )
        other_trip = Trip(
            id=uuid4(),
            status=TripStatus.active,
            start_address_encrypted="other_trip_start",
            purpose="Other business meeting",
            rate_customization_id=other_customization.id,
            rate_category_id=other_category.id,
            reimbursement_rate=0.67,
            user_id=other_user.id
        )
        test_db_session.add_all([user_trip, other_trip])
        await test_db_session.commit()
        
        repo = TripRepo(test_db_session)
        
        # Get trips for test_user
        user_trips = await repo.get_user_trips(test_user.id)
        assert len(user_trips) == 1
        assert user_trips[0].id == user_trip.id
        assert user_trips[0].purpose == "User business meeting"
        assert user_trips[0].user_id == test_user.id
        
        # Get trips for other_user
        other_trips = await repo.get_user_trips(other_user.id)
        assert len(other_trips) == 1
        assert other_trips[0].id == other_trip.id
        assert other_trips[0].purpose == "Other business meeting"
        assert other_trips[0].user_id == other_user.id
