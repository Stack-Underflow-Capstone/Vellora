import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError

from app.modules.trips.schemas import (
    CreateTripDTO,
    EditTripDTO,
    EndTripDTO,
    ManualCreateTripDTO,
    TripResponseDTO,
    ExpenseResponseDTO
)
from app.modules.trips.models import TripStatus


class TestCreateTripDTO:

    def test_create_trip_dto_valid(self):
        customization_id = uuid4()
        category_id = uuid4()

        vehicle_id = uuid4()
        dto = CreateTripDTO(
            start_address="123 Main St",
            purpose="Business meeting",
            vehicle_id=vehicle_id,
            rate_customization_id=customization_id,
            rate_category_id=category_id
        )

        assert dto.start_address == "123 Main St"
        assert dto.purpose == "Business meeting"
        assert dto.vehicle_id == vehicle_id
        assert dto.rate_customization_id == customization_id
        assert dto.rate_category_id == category_id

    def test_create_trip_dto_missing_required_fields(self):
        with pytest.raises(ValidationError):
            CreateTripDTO(start_address="123 Main St")

    def test_create_trip_dto_optional_purpose(self):
        customization_id = uuid4()
        category_id = uuid4()

        dto = CreateTripDTO(
            start_address="123 Main St",
            rate_customization_id=customization_id,
            rate_category_id=category_id
        )

        assert dto.start_address == "123 Main St"
        assert dto.purpose is None
        assert dto.vehicle_id is None


class TestEndTripDTO:

    def test_end_trip_dto_valid(self):
        dto = EndTripDTO(
            end_address="456 Oak Ave",
            geometry={"type":"LineString","coordinates":[[-122.4194,37.7749],[-122.4094,37.7849]]},
            distance_meters=81320.0
        )

        assert dto.end_address == "456 Oak Ave"
        assert dto.geometry == {"type":"LineString","coordinates":[[-122.4194,37.7749],[-122.4094,37.7849]]}
        assert dto.distance_meters == 81320.0
        assert dto.miles == 50.53

    def test_end_trip_dto_missing_required_fields(self):
        with pytest.raises(ValidationError):
            EndTripDTO(end_address="456 Oak Ave")
        
        with pytest.raises(ValidationError):
            EndTripDTO(distance_meters=81320.0)
    
    def test_end_trip_dto_negative_distance(self):
        with pytest.raises(ValidationError) as exc_info:
            EndTripDTO(end_address="456 Oak Ave", distance_meters=-100.0)
        assert "Distance must be non-negative" in str(exc_info.value)


class TestEditTripDTO:

    def test_edit_trip_dto_all_fields(self):
        customization_id = uuid4()
        category_id = uuid4()
        vehicle_id = uuid4()

        dto = EditTripDTO(
            purpose="Updated purpose",
            vehicle_id=vehicle_id,
            rate_customization_id=customization_id,
            rate_category_id=category_id
        )

        assert dto.purpose == "Updated purpose"
        assert dto.vehicle_id == vehicle_id
        assert dto.rate_customization_id == customization_id
        assert dto.rate_category_id == category_id

    def test_edit_trip_dto_partial_fields(self):
        vehicle_id = uuid4()
        dto1 = EditTripDTO(purpose="Updated")
        dto2 = EditTripDTO(rate_customization_id=uuid4())
        dto3 = EditTripDTO(rate_category_id=uuid4())
        dto4 = EditTripDTO(vehicle_id=vehicle_id)

        assert dto1.purpose == "Updated"
        assert dto1.vehicle_id is None
        assert dto4.vehicle_id == vehicle_id
        assert dto4.purpose is None
        assert dto1.rate_customization_id is None
        assert dto1.rate_category_id is None

        assert dto2.purpose is None
        assert dto2.rate_customization_id is not None
        
        assert dto3.rate_category_id is not None

    def test_edit_trip_dto_empty(self):
        dto = EditTripDTO()

        assert dto.purpose is None
        assert dto.rate_customization_id is None
        assert dto.rate_category_id is None


class TestManualCreateTripDTO:

    def test_manual_create_trip_dto_valid(self):
        started_time = datetime.now(timezone.utc)
        ended_time = started_time + timedelta(hours=2)
        customization_id = uuid4()
        category_id = uuid4()

        vehicle_id = uuid4()
        dto = ManualCreateTripDTO(
            start_address="123 Main St",
            end_address="456 Oak Ave",
            purpose="Client meeting",
            vehicle_id=vehicle_id,
            miles=25.5,
            geometry={"type":"LineString","coordinates":[[-122.4194,37.7749],[-122.4094,37.7849]]},
            started_at=started_time,
            ended_at=ended_time,
            rate_customization_id=customization_id,
            rate_category_id=category_id
        )

        assert dto.start_address == "123 Main St"
        assert dto.end_address == "456 Oak Ave"
        assert dto.purpose == "Client meeting"
        assert dto.vehicle_id == vehicle_id
        assert dto.miles == 25.5
        assert dto.started_at == started_time
        assert dto.ended_at == ended_time
        assert dto.rate_customization_id == customization_id
        assert dto.rate_category_id == category_id

    def test_manual_create_trip_dto_optional_fields(self):
        started_time = datetime.now(timezone.utc)
        ended_time = started_time + timedelta(hours=1)

        dto = ManualCreateTripDTO(
            start_address="123 Main St",
            end_address="456 Oak Ave",
            miles=10.0,
            started_at=started_time,
            ended_at=ended_time,
            rate_customization_id=uuid4(),
            rate_category_id=uuid4()
        )

        assert dto.purpose is None
        assert dto.vehicle_id is None
        assert dto.geometry is None

    def test_manual_create_trip_dto_with_expenses(self):
        started_time = datetime.now(timezone.utc)
        ended_time = started_time + timedelta(hours=1)
        
        dto = ManualCreateTripDTO(
            start_address="123 Main St",
            end_address="456 Oak Ave",
            miles=10.5,
            started_at=started_time,
            ended_at=ended_time,
            rate_customization_id=uuid4(),
            rate_category_id=uuid4(),
            expenses=[
                {"type": "Parking", "amount": 15.50},
                {"type": "Toll", "amount": 5.75}
            ]
        )
        
        assert len(dto.expenses) == 2
        assert dto.expenses[0].type == "Parking"
        assert dto.expenses[0].amount == 15.50
        assert dto.expenses[1].type == "Toll"
        assert dto.expenses[1].amount == 5.75

    def test_manual_create_trip_dto_missing_required_fields(self):
        with pytest.raises(ValidationError):
            ManualCreateTripDTO(
                start_address="123 Main St",
                # Missing end_address, miles, times, etc.
            )


class TestExpenseResponseDTO:

    def test_expense_response_dto_valid(self):
        expense_id = uuid4()
        created_at = datetime.now(timezone.utc)

        dto = ExpenseResponseDTO(
            id=str(expense_id),
            type="Parking",
            amount=15.50,
            created_at=created_at
        )

        assert dto.id == str(expense_id)
        assert dto.type == "Parking"
        assert dto.amount == 15.50
        assert dto.created_at == created_at


class TestTripResponseDTO:

    def test_trip_response_dto_valid(self):
        trip_id = uuid4()
        customization_id = uuid4()
        category_id = uuid4()
        started_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)

        dto = TripResponseDTO(
            id=str(trip_id),
            status=TripStatus.active,
            start_address="123 Main St",
            purpose="Business",
            reimbursement_rate=0.65,
            started_at=started_at,
            updated_at=updated_at,
            rate_customization_id=customization_id,
            rate_category_id=category_id
        )

        assert dto.id == str(trip_id)
        assert dto.status == TripStatus.active
        assert dto.start_address == "123 Main St"
        assert dto.purpose == "Business"
        assert dto.reimbursement_rate == 0.65

    def test_trip_response_dto_from_orm(self):
        from unittest.mock import MagicMock, patch
        from app.modules.trips.models import Trip
        from app.modules.vehicles.models import Vehicle
        
        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.id = uuid4()
        mock_vehicle.name = "Honda Civic"
        mock_vehicle.license_plate = "ABC123"
        mock_vehicle.model = "Civic"
        
        mock_trip = MagicMock(spec=Trip)
        mock_trip.id = uuid4()
        mock_trip.status = TripStatus.active
        mock_trip.start_address_encrypted = "encrypted_start"
        mock_trip.end_address_encrypted = None
        mock_trip.purpose = "Business"
        mock_trip.vehicle_id = mock_vehicle.id
        mock_trip.vehicle = mock_vehicle
        mock_trip.miles = None
        mock_trip.reimbursement_rate = 0.65
        mock_trip.mileage_reimbursement_total = None
        mock_trip.expense_reimbursement_total = None
        mock_trip.started_at = datetime.now(timezone.utc)
        mock_trip.scheduled_start_at = None
        mock_trip.scheduled_end_at = None
        mock_trip.ended_at = None
        mock_trip.updated_at = datetime.now(timezone.utc)
        mock_trip.rate_customization_id = uuid4()
        mock_trip.rate_category_id = uuid4()
        mock_trip.geometry_encrypted = None
        mock_trip.expenses = []
        mock_trip.calendar_provider = None
        mock_trip.calendar_event_id = None
        mock_trip.calendar_event_url = None

        with patch('app.modules.trips.schemas.decrypt_address', return_value="123 Main St"):
            dto = TripResponseDTO.model_validate(mock_trip)

        assert str(mock_trip.id) == dto.id
        assert dto.status == TripStatus.active
        assert dto.start_address == "123 Main St"
        assert dto.total_reimbursement == 0

    def test_trip_response_dto_with_expenses(self):
        from unittest.mock import MagicMock, patch
        from app.modules.trips.models import Trip
        from app.modules.expenses.models import Expense
        from app.modules.vehicles.models import Vehicle
        
        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.id = uuid4()
        mock_vehicle.name = "Toyota Prius"
        mock_vehicle.license_plate = "XYZ789"
        mock_vehicle.model = "Prius"
        
        mock_expense1 = MagicMock(spec=Expense)
        mock_expense1.id = uuid4()
        mock_expense1.type = "Parking"
        mock_expense1.amount = 15.50
        mock_expense1.created_at = datetime.now(timezone.utc)

        mock_expense2 = MagicMock(spec=Expense)
        mock_expense2.id = uuid4()
        mock_expense2.type = "Tolls"
        mock_expense2.amount = 5.00
        mock_expense2.created_at = datetime.now(timezone.utc)

        mock_trip = MagicMock(spec=Trip)
        mock_trip.id = uuid4()
        mock_trip.status = TripStatus.completed
        mock_trip.start_address_encrypted = "encrypted_start"
        mock_trip.end_address_encrypted = "encrypted_end"
        mock_trip.purpose = "Business"
        mock_trip.vehicle_id = mock_vehicle.id
        mock_trip.vehicle = mock_vehicle
        mock_trip.miles = 50.0
        mock_trip.reimbursement_rate = 0.65
        mock_trip.mileage_reimbursement_total = 32.50
        mock_trip.expense_reimbursement_total = 20.50
        mock_trip.started_at = datetime.now(timezone.utc)
        mock_trip.scheduled_start_at = None
        mock_trip.scheduled_end_at = None
        mock_trip.ended_at = datetime.now(timezone.utc)
        mock_trip.updated_at = datetime.now(timezone.utc)
        mock_trip.rate_customization_id = uuid4()
        mock_trip.rate_category_id = uuid4()
        mock_trip.geometry_encrypted = None
        mock_trip.expenses = [mock_expense1, mock_expense2]
        mock_trip.calendar_provider = None
        mock_trip.calendar_event_id = None
        mock_trip.calendar_event_url = None

        with patch('app.modules.trips.schemas.decrypt_address', side_effect=["123 Main St", "456 Oak Ave"]):
            dto = TripResponseDTO.model_validate(mock_trip)

        assert dto.status == TripStatus.completed
        assert dto.miles == 50.0
        assert dto.total_reimbursement == 53.0
        assert len(dto.expenses) == 2
        assert dto.expenses[0].type == "Parking"
        assert dto.expenses[1].type == "Tolls"

    def test_trip_response_dto_missing_required_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            TripResponseDTO(
                id=str(uuid4()),
                status=TripStatus.active
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("started_at",) for error in errors)
        assert any(error["loc"] == ("updated_at",) for error in errors)
        assert any(error["loc"] == ("rate_customization_id",) for error in errors)
        assert any(error["loc"] == ("rate_category_id",) for error in errors)
