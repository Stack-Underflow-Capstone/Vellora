import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi import status, HTTPException

from app.modules.common_places.router import get_common_place_service
from app.modules.common_places.service import CommonPlaceService
from app.modules.common_places.schemas import CommonPlaceCreate, CommonPlaceUpdate, CommonPlaceResponse
from app.modules.common_places.models import CommonPlace
from app.modules.common_places.exceptions import (
    CommonPlaceNotFoundError,
    InvalidCommonPlaceDataError,
    DuplicateCommonPlaceError,
    MaxCommonPlacesError,
)
from app.modules.users.models import User, UserRole


class TestCreateCommonPlaceEndpoint:
    """POST /common-places/ endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=CommonPlaceService)

    @pytest.fixture
    def mock_place(self):
        place = MagicMock(spec=CommonPlace)
        place.id = uuid4()
        place.user_id = uuid4()
        place.name = "Home"
        place.address = "encrypted_address"
        return place

    @pytest.mark.asyncio
    async def test_create_common_place_success(self, mock_service, mock_place, mock_user):
        from app.modules.common_places.router import create_common_place
        
        request_body = {"name": "Home", "address": "123 Main St"}
        mock_service.create_common_place.return_value = mock_place

        # Mock model_validate to bypass decryption logic in schema
        with patch('app.modules.common_places.router.CommonPlaceResponse.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await create_common_place(
                body=CommonPlaceCreate(**request_body),
                svc=mock_service,
                current_user=mock_user
            )

        mock_service.create_common_place.assert_called_once_with(mock_user.id, CommonPlaceCreate(**request_body))
        mock_validate.assert_called_once_with(mock_place)

    @pytest.mark.asyncio
    async def test_create_common_place_max_limit(self, mock_service, mock_user):
        from app.modules.common_places.router import create_common_place

        request_body = {"name": "Gym", "address": "456 Fit St"}
        mock_service.create_common_place.side_effect = MaxCommonPlacesError("Maximum of 4 common places allowed")

        with pytest.raises(HTTPException) as exc_info:
            await create_common_place(
                body=CommonPlaceCreate(**request_body),
                svc=mock_service,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == 400
        assert "Maximum of 4 common places allowed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_common_place_duplicate_name(self, mock_service, mock_user):
        from app.modules.common_places.router import create_common_place

        request_body = {"name": "Home", "address": "New Address"}
        mock_service.create_common_place.side_effect = DuplicateCommonPlaceError("A common place with this name already exists")

        with pytest.raises(HTTPException) as exc_info:
            await create_common_place(
                body=CommonPlaceCreate(**request_body),
                svc=mock_service,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_create_common_place_invalid_data(self, mock_service, mock_user):
        from app.modules.common_places.router import create_common_place

        request_body = {"name": "", "address": "123 Main St"}
        mock_service.create_common_place.side_effect = InvalidCommonPlaceDataError("Name is required")

        with pytest.raises(HTTPException) as exc_info:
            await create_common_place(
                body=CommonPlaceCreate(**request_body),
                svc=mock_service,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == 400


class TestGetCommonPlacesEndpoint:
    """GET /common-places/ endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=CommonPlaceService)

    @pytest.fixture
    def mock_places(self):
        places = []
        for i in range(3):
            place = MagicMock(spec=CommonPlace)
            place.id = uuid4()
            place.user_id = uuid4()
            place.name = f"Place {i}"
            place.address = f"encrypted_address_{i}"
            places.append(place)
        return places

    @pytest.mark.asyncio
    async def test_get_common_places_success(self, mock_service, mock_places, mock_user):
        from app.modules.common_places.router import get_user_common_places

        mock_service.get_all_common_places.return_value = mock_places

        with patch('app.modules.common_places.router.CommonPlaceResponse.model_validate') as mock_validate:
            mock_validate.side_effect = lambda x: MagicMock() # Return a mock for each place
            result = await get_user_common_places(svc=mock_service, current_user=mock_user)

        assert len(result) == 3
        mock_service.get_all_common_places.assert_called_once_with(mock_user.id)
        assert mock_validate.call_count == 3

    @pytest.mark.asyncio
    async def test_get_common_places_empty(self, mock_service, mock_user):
        from app.modules.common_places.router import get_user_common_places

        mock_service.get_all_common_places.return_value = []

        result = await get_user_common_places(svc=mock_service, current_user=mock_user)

        assert result == []


class TestGetCommonPlaceEndpoint:
    """GET /common-places/{place_id} endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=CommonPlaceService)

    @pytest.fixture
    def mock_place(self):
        place = MagicMock(spec=CommonPlace)
        place.id = uuid4()
        place.user_id = uuid4()
        place.name = "Work"
        place.address = "encrypted_work_address"
        return place

    @pytest.mark.asyncio
    async def test_get_common_place_success(self, mock_service, mock_place, mock_user):
        from app.modules.common_places.router import get_common_place

        place_id = uuid4()
        mock_service.get_common_place.return_value = mock_place

        with patch('app.modules.common_places.router.CommonPlaceResponse.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await get_common_place(place_id=place_id, svc=mock_service, current_user=mock_user)

        mock_service.get_common_place.assert_called_once_with(mock_user.id, place_id)
        mock_validate.assert_called_once_with(mock_place)

    @pytest.mark.asyncio
    async def test_get_common_place_not_found(self, mock_service, mock_user):
        from app.modules.common_places.router import get_common_place

        place_id = uuid4()
        mock_service.get_common_place.side_effect = CommonPlaceNotFoundError("Common place not found")

        with pytest.raises(HTTPException) as exc_info:
            await get_common_place(place_id=place_id, svc=mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 404


class TestUpdateCommonPlaceEndpoint:
    """PATCH /common-places/{place_id} endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=CommonPlaceService)

    @pytest.fixture
    def mock_place(self):
        place = MagicMock(spec=CommonPlace)
        place.id = uuid4()
        place.user_id = uuid4()
        place.name = "Updated Name"
        place.address = "encrypted_updated_address"
        return place

    @pytest.mark.asyncio
    async def test_update_common_place_success(self, mock_service, mock_place, mock_user):
        from app.modules.common_places.router import update_common_place

        place_id = uuid4()
        request_body = {"name": "Updated Name"}
        mock_service.update_common_place.return_value = mock_place

        with patch('app.modules.common_places.router.CommonPlaceResponse.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await update_common_place(
                place_id=place_id,
                body=CommonPlaceUpdate(**request_body),
                svc=mock_service,
                current_user=mock_user
            )

        mock_service.update_common_place.assert_called_once_with(mock_user.id, place_id, CommonPlaceUpdate(**request_body))
        mock_validate.assert_called_once_with(mock_place)

    @pytest.mark.asyncio
    async def test_update_common_place_duplicate_name(self, mock_service, mock_user):
        from app.modules.common_places.router import update_common_place

        place_id = uuid4()
        request_body = {"name": "Existing Name"}
        mock_service.update_common_place.side_effect = DuplicateCommonPlaceError("Name already exists")

        with pytest.raises(HTTPException) as exc_info:
            await update_common_place(
                place_id=place_id,
                body=CommonPlaceUpdate(**request_body),
                svc=mock_service,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_update_common_place_not_found(self, mock_service, mock_user):
        from app.modules.common_places.router import update_common_place

        place_id = uuid4()
        request_body = {"name": "New Name"}
        mock_service.update_common_place.side_effect = CommonPlaceNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await update_common_place(
                place_id=place_id,
                body=CommonPlaceUpdate(**request_body),
                svc=mock_service,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == 404


class TestDeleteCommonPlaceEndpoint:
    """DELETE /common-places/{place_id} endpoint"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=CommonPlaceService)

    @pytest.mark.asyncio
    async def test_delete_common_place_success(self, mock_service, mock_user):
        from app.modules.common_places.router import delete_common_place

        place_id = uuid4()
        mock_service.delete_common_place.return_value = None

        result = await delete_common_place(place_id=place_id, svc=mock_service, current_user=mock_user)

        assert result.status_code == status.HTTP_204_NO_CONTENT
        mock_service.delete_common_place.assert_called_once_with(mock_user.id, place_id)

    @pytest.mark.asyncio
    async def test_delete_common_place_not_found(self, mock_service, mock_user):
        from app.modules.common_places.router import delete_common_place

        place_id = uuid4()
        mock_service.delete_common_place.side_effect = CommonPlaceNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await delete_common_place(place_id=place_id, svc=mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 404


class TestGetCommonPlacesServiceDependency:

    def test_get_common_place_service_returns_service(self):
        mock_db = MagicMock()

        service = get_common_place_service(db=mock_db)

        assert isinstance(service, CommonPlaceService)
        assert service.commonplace_repo is not None
