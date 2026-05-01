import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError

from app.modules.rate_categories.schemas import (
    CreateRateCategoryDTO,
    EditRateCategoryDTO,
    RateCategoryResponseDTO
)


class TestCreateRateCategoryDTO:

    def test_create_category_dto_valid(self):
        data = {"name": "Standard", "cost_per_mile": 0.65}
        
        dto = CreateRateCategoryDTO(**data)
        
        assert dto.name == "Standard"
        assert dto.cost_per_mile == 0.65

    def test_create_category_dto_missing_required_fields(self):
        with pytest.raises(ValidationError):
            CreateRateCategoryDTO(name="Standard")
        
        with pytest.raises(ValidationError):
            CreateRateCategoryDTO(cost_per_mile=0.65)


class TestEditRateCategoryDTO:

    def test_edit_category_dto_all_fields(self):
        dto = EditRateCategoryDTO(name="Premium", cost_per_mile=0.85)
        
        assert dto.name == "Premium"
        assert dto.cost_per_mile == 0.85

    def test_edit_category_dto_partial_fields(self):
        dto1 = EditRateCategoryDTO(name="Premium")
        assert dto1.name == "Premium"
        assert dto1.cost_per_mile is None
        
        dto2 = EditRateCategoryDTO(cost_per_mile=0.85)
        assert dto2.name is None
        assert dto2.cost_per_mile == 0.85

    def test_edit_category_dto_empty(self):
        dto = EditRateCategoryDTO()
        
        assert dto.name is None
        assert dto.cost_per_mile is None


class TestRateCategoryResponseDTO:

    def test_response_dto_valid(self):
        category_id = uuid4()
        customization_id = uuid4()
        created_at = datetime.now(timezone.utc)
        
        dto = RateCategoryResponseDTO(
            id=category_id,
            name="Standard",
            cost_per_mile=0.65,
            created_at=created_at,
            rate_customization_id=customization_id
        )
        
        assert dto.id == category_id
        assert dto.name == "Standard"
        assert dto.cost_per_mile == 0.65
        assert dto.created_at == created_at
        assert dto.rate_customization_id == customization_id

    def test_response_dto_from_orm(self):
        from unittest.mock import MagicMock
        from app.modules.rate_categories.models import RateCategory
        
        category_id = uuid4()
        customization_id = uuid4()
        created_at = datetime.now(timezone.utc)
        
        mock_category = MagicMock(spec=RateCategory)
        mock_category.id = category_id
        mock_category.name = "Standard"
        mock_category.cost_per_mile = 0.65
        mock_category.created_at = created_at
        mock_category.rate_customization_id = customization_id
        
        dto = RateCategoryResponseDTO.model_validate(mock_category)
        
        assert dto.id == category_id
        assert dto.name == "Standard"
        assert dto.cost_per_mile == 0.65
        assert dto.created_at == created_at
        assert dto.rate_customization_id == customization_id

    def test_response_dto_missing_required_fields(self):
        with pytest.raises(ValidationError):
            RateCategoryResponseDTO(
                name="Standard",
                cost_per_mile=0.65,
                created_at=datetime.now(timezone.utc),
                rate_customization_id=uuid4()
            )
