import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from app.modules.rate_customizations.schemas import (
    CreateRateCustomizationDTO,
    EditRateCustomizationDTO,
    RateCustomizationResponseDTO
)


class TestCreateRateCustomizationDTO:

    def test_create_customization_dto_valid(self):
        dto = CreateRateCustomizationDTO(
            name="Business Rates 2024",
            description="Standard business mileage rates",
            year=2024
        )

        assert dto.name == "Business Rates 2024"
        assert dto.description == "Standard business mileage rates"
        assert dto.year == 2024

    def test_create_customization_dto_missing_required_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            CreateRateCustomizationDTO(name="Test")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("year",) for error in errors)

    def test_create_customization_dto_optional_description(self):
        dto = CreateRateCustomizationDTO(
            name="Business Rates 2024",
            year=2024
        )

        assert dto.name == "Business Rates 2024"
        assert dto.description is None
        assert dto.year == 2024


class TestEditRateCustomizationDTO:

    def test_edit_customization_dto_all_fields(self):
        dto = EditRateCustomizationDTO(
            name="Updated Name",
            description="Updated Description",
            year=2025
        )

        assert dto.name == "Updated Name"
        assert dto.description == "Updated Description"
        assert dto.year == 2025

    def test_edit_customization_dto_partial_fields(self):
        dto = EditRateCustomizationDTO(name="Updated Name")

        assert dto.name == "Updated Name"
        assert dto.description is None
        assert dto.year is None

    def test_edit_customization_dto_empty(self):
        dto = EditRateCustomizationDTO()

        assert dto.name is None
        assert dto.description is None
        assert dto.year is None


class TestRateCustomizationResponseDTO:

    def test_response_dto_valid(self):
        customization_id = uuid4()
        created_at = datetime.now()

        dto = RateCustomizationResponseDTO(
            id=customization_id,
            name="Business Rates 2024",
            year=2024,
            created_at=created_at
        )

        assert dto.id == customization_id
        assert dto.name == "Business Rates 2024"
        assert dto.year == 2024
        assert dto.created_at == created_at

    def test_response_dto_from_orm(self):
        from unittest.mock import MagicMock
        from app.modules.rate_customizations.models import RateCustomization
        
        mock_customization = MagicMock(spec=RateCustomization)
        mock_customization.id = uuid4()
        mock_customization.name = "Business Rates 2024"
        mock_customization.year = 2024
        mock_customization.created_at = datetime.now()

        dto = RateCustomizationResponseDTO.model_validate(mock_customization)

        assert dto.id == mock_customization.id
        assert dto.name == mock_customization.name
        assert dto.year == mock_customization.year
        assert dto.created_at == mock_customization.created_at

    def test_response_dto_missing_required_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            RateCustomizationResponseDTO(
                id=uuid4(),
                name="Test"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("year",) for error in errors)
        assert any(error["loc"] == ("created_at",) for error in errors)
