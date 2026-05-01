import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError
from unittest.mock import MagicMock, patch

from app.modules.common_places.schemas import CommonPlaceCreate, CommonPlaceUpdate, CommonPlaceResponse


class TestCommonPlaceCreate:

    def test_create_common_place_valid(self):
        data = {"name": "Home", "address": "123 Main St"}
        
        dto = CommonPlaceCreate(**data)
        
        assert dto.name == "Home"
        assert dto.address == "123 Main St"

    def test_create_common_place_missing_required_fields(self):
        with pytest.raises(ValidationError):
            CommonPlaceCreate(name="Home")
        
        with pytest.raises(ValidationError):
            CommonPlaceCreate(address="123 Main St")


class TestCommonPlaceUpdate:

    def test_update_common_place_all_fields(self):
        dto = CommonPlaceUpdate(name="Work", address="456 Office Blvd")
        
        assert dto.name == "Work"
        assert dto.address == "456 Office Blvd"

    def test_update_common_place_partial_fields(self):
        dto1 = CommonPlaceUpdate(name="Work")
        assert dto1.name == "Work"
        assert dto1.address is None
        
        dto2 = CommonPlaceUpdate(address="456 Office Blvd")
        assert dto2.name is None
        assert dto2.address == "456 Office Blvd"

    def test_update_common_place_empty(self):
        dto = CommonPlaceUpdate()
        
        assert dto.name is None
        assert dto.address is None


class TestCommonPlaceResponse:

    def test_common_place_response_valid(self):
        user_id = uuid4()
        place_id = uuid4()
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)
        
        dto = CommonPlaceResponse(
            user_id=user_id,
            id=place_id,
            name="Home",
            address="123 Main St",
            created_at=created_at,
            updated_at=updated_at
        )
        
        assert dto.user_id == user_id
        assert dto.id == place_id
        assert dto.name == "Home"
        assert dto.address == "123 Main St"
        assert dto.created_at == created_at
        assert dto.updated_at == updated_at

    def test_common_place_response_model_validate(self):
        from app.modules.common_places.models import CommonPlace
        
        user_id = uuid4()
        place_id = uuid4()
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)
        
        mock_place = MagicMock(spec=CommonPlace)
        mock_place.user_id = user_id
        mock_place.id = place_id
        mock_place.name = "Home"
        mock_place.address = "encrypted_address"
        mock_place.created_at = created_at
        mock_place.updated_at = updated_at
        
        with patch("app.modules.common_places.schemas.decrypt_address", return_value="Decrypted Address"):
            dto = CommonPlaceResponse.model_validate(mock_place)
        
        assert dto.user_id == user_id
        assert dto.id == place_id
        assert dto.name == "Home"
        assert dto.address == "Decrypted Address"
        assert dto.created_at == created_at
        assert dto.updated_at == updated_at

    def test_common_place_response_missing_required_fields(self):
        with pytest.raises(ValidationError):
            CommonPlaceResponse(
                id=uuid4(),
                name="Home",
                address="123 Main St",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
