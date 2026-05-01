import pytest
from uuid import uuid4
from pydantic import ValidationError

from app.modules.vehicles.schemas import CreateVehicleDTO, EditVehicleDTO, VehicleResponse


class TestCreateVehicleDTO:

    def test_create_vehicle_dto_valid(self):
        dto = CreateVehicleDTO(
            name="Personal Car",
            license_plate="ABC123",
            model="Toyota Camry",
            year=2020,
            color="Blue"
        )

        assert dto.name == "Personal Car"
        assert dto.license_plate == "ABC123"
        assert dto.model == "Toyota Camry"
        assert dto.year == 2020
        assert dto.color == "Blue"

    def test_create_vehicle_dto_required_fields_only(self):
        dto = CreateVehicleDTO(
            name="Work Truck",
            license_plate="XYZ789",
            model="Ford F-150"
        )

        assert dto.name == "Work Truck"
        assert dto.license_plate == "XYZ789"
        assert dto.model == "Ford F-150"
        assert dto.year is None
        assert dto.color is None

    def test_create_vehicle_dto_missing_required_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            CreateVehicleDTO(name="Car", license_plate="ABC123")
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" and "model" in error["loc"] for error in errors)

    def test_create_vehicle_dto_empty_name(self):
        # Empty strings are allowed in the current schema
        dto = CreateVehicleDTO(
            name="",
            license_plate="ABC123",
            model="Toyota"
        )
        assert dto.name == ""

    def test_create_vehicle_dto_empty_license_plate(self):
        # Empty strings are allowed in the current schema  
        dto = CreateVehicleDTO(
            name="My Car",
            license_plate="",
            model="Toyota"
        )
        assert dto.license_plate == ""

    def test_create_vehicle_dto_empty_model(self):
        # Empty strings are allowed in the current schema
        dto = CreateVehicleDTO(
            name="My Car",
            license_plate="ABC123",
            model=""
        )
        assert dto.model == ""

    def test_create_vehicle_dto_negative_year(self):
        # Negative years are allowed in the current schema
        dto = CreateVehicleDTO(
            name="My Car",
            license_plate="ABC123",
            model="Toyota",
            year=-2020
        )
        assert dto.year == -2020


class TestEditVehicleDTO:

    def test_edit_vehicle_dto_all_fields(self):
        dto = EditVehicleDTO(
            name="Updated Car",
            license_plate="NEW123",
            model="Honda Accord",
            year=2023,
            color="Red",
            is_active=True
        )

        assert dto.name == "Updated Car"
        assert dto.license_plate == "NEW123"
        assert dto.model == "Honda Accord"
        assert dto.year == 2023
        assert dto.color == "Red"
        assert dto.is_active is True

    def test_edit_vehicle_dto_partial_fields(self):
        dto1 = EditVehicleDTO(name="New Name")
        dto2 = EditVehicleDTO(license_plate="NEW456")
        dto3 = EditVehicleDTO(year=2024)
        dto4 = EditVehicleDTO(is_active=False)

        assert dto1.name == "New Name"
        assert dto1.license_plate is None
        assert dto1.model is None
        
        assert dto2.license_plate == "NEW456"
        assert dto2.name is None
        
        assert dto3.year == 2024
        assert dto3.color is None
        
        assert dto4.is_active is False
        assert dto4.year is None

    def test_edit_vehicle_dto_empty(self):
        dto = EditVehicleDTO()

        assert dto.name is None
        assert dto.license_plate is None
        assert dto.model is None
        assert dto.year is None
        assert dto.color is None
        assert dto.is_active is None

    def test_edit_vehicle_dto_negative_year(self):
        # Negative years are allowed in the current schema
        dto = EditVehicleDTO(year=-2020)
        assert dto.year == -2020


class TestVehicleResponse:

    def test_vehicle_response_valid(self):
        from datetime import datetime, timezone
        
        vehicle_id = uuid4()
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)

        response = VehicleResponse(
            id=vehicle_id,
            name="Test Car",
            license_plate="TST123",
            model="Test Model",
            year=2022,
            color="Blue",
            is_active=True,
            created_at=created_at,
            updated_at=updated_at
        )

        assert response.id == vehicle_id
        assert response.name == "Test Car"
        assert response.license_plate == "TST123"
        assert response.model == "Test Model"
        assert response.year == 2022
        assert response.color == "Blue"
        assert response.is_active is True
        assert response.created_at == created_at
        assert response.updated_at == updated_at

    def test_vehicle_response_optional_fields_none(self):
        from datetime import datetime, timezone
        
        vehicle_id = uuid4()
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)

        response = VehicleResponse(
            id=vehicle_id,
            name="Test Car",
            license_plate="TST123",
            model="Test Model",
            year=None,
            color=None,
            is_active=True,
            created_at=created_at,
            updated_at=updated_at
        )

        assert response.year is None
        assert response.color is None
        assert response.is_active is True

    def test_vehicle_response_from_orm_attributes(self):
        from unittest.mock import MagicMock
        from datetime import datetime, timezone
        from app.modules.vehicles.models import Vehicle
        
        mock_vehicle = MagicMock(spec=Vehicle)
        mock_vehicle.id = uuid4()
        mock_vehicle.name = "ORM Car"
        mock_vehicle.license_plate = "ORM123"
        mock_vehicle.model = "ORM Model"
        mock_vehicle.year = 2021
        mock_vehicle.color = "Green"
        mock_vehicle.is_active = True
        mock_vehicle.created_at = datetime.now(timezone.utc)
        mock_vehicle.updated_at = datetime.now(timezone.utc)

        response = VehicleResponse.model_validate(mock_vehicle)

        assert response.id == mock_vehicle.id
        assert response.name == "ORM Car"
        assert response.license_plate == "ORM123"
        assert response.model == "ORM Model"
        assert response.year == 2021
        assert response.color == "Green"
        assert response.is_active is True

    def test_vehicle_response_missing_required_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            VehicleResponse(
                name="Incomplete Car",
                license_plate="INC123"
                # Missing required fields: id, model, is_active, created_at, updated_at
            )
        
        errors = exc_info.value.errors()
        required_fields = ["id", "model", "is_active", "created_at", "updated_at"]
        for field in required_fields:
            assert any(error["type"] == "missing" and field in error["loc"] for error in errors)