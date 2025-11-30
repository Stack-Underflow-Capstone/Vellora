import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

from app.modules.common_places.service import CommonPlaceService
from app.modules.common_places.repository import CommonPlaceRepo
from app.modules.common_places.schemas import CommonPlaceCreate, CommonPlaceUpdate
from app.modules.common_places.models import CommonPlace
from app.modules.common_places.exceptions import (
    CommonPlaceNotFoundError,
    DuplicateCommonPlaceError,
    MaxCommonPlacesError,
    CommonPlacePersistenceError
)


class TestCommonPlaceServiceCreate:

    @pytest.fixture
    def repo(self):
        return AsyncMock(spec=CommonPlaceRepo)

    @pytest.fixture
    def service(self, repo):
        return CommonPlaceService(repo)

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.mark.asyncio
    async def test_create_common_place_success(self, service, repo, user_id):
        dto = CommonPlaceCreate(name="Home", address="123 Main St")
        repo.get_all_by_user.return_value = []
        repo.get_by_user_and_commonplace_name.return_value = None
        
        mock_place = MagicMock(spec=CommonPlace)
        repo.create.return_value = mock_place

        with patch("app.modules.common_places.service.encrypt_address", return_value="encrypted_address"):
            result = await service.create_common_place(user_id, dto)

        assert result == mock_place
        repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_common_place_max_limit(self, service, repo, user_id):
        dto = CommonPlaceCreate(name="Home", address="123 Main St")
        repo.get_all_by_user.return_value = [MagicMock() for _ in range(4)]

        with pytest.raises(MaxCommonPlacesError):
            await service.create_common_place(user_id, dto)

    @pytest.mark.asyncio
    async def test_create_common_place_duplicate_name(self, service, repo, user_id):
        dto = CommonPlaceCreate(name="Home", address="123 Main St")
        repo.get_all_by_user.return_value = []
        repo.get_by_user_and_commonplace_name.return_value = MagicMock()

        with pytest.raises(DuplicateCommonPlaceError):
            await service.create_common_place(user_id, dto)

    @pytest.mark.asyncio
    async def test_create_common_place_integrity_error(self, service, repo, user_id):
        dto = CommonPlaceCreate(name="Home", address="123 Main St")
        repo.get_all_by_user.return_value = []
        repo.get_by_user_and_commonplace_name.return_value = None
        repo.create.side_effect = IntegrityError("Duplicate", params={}, orig=None)

        with patch("app.modules.common_places.service.encrypt_address", return_value="encrypted_address"):
            with pytest.raises(DuplicateCommonPlaceError):
                await service.create_common_place(user_id, dto)


class TestCommonPlaceServiceGetAll:

    @pytest.fixture
    def repo(self):
        return AsyncMock(spec=CommonPlaceRepo)

    @pytest.fixture
    def service(self, repo):
        return CommonPlaceService(repo)

    @pytest.mark.asyncio
    async def test_get_all_common_places(self, service, repo):
        user_id = uuid4()
        mock_places = [MagicMock(), MagicMock()]
        repo.get_all_by_user.return_value = mock_places

        result = await service.get_all_common_places(user_id)

        assert result == mock_places
        repo.get_all_by_user.assert_called_once_with(user_id)


class TestCommonPlaceServiceGetOne:

    @pytest.fixture
    def repo(self):
        return AsyncMock(spec=CommonPlaceRepo)

    @pytest.fixture
    def service(self, repo):
        return CommonPlaceService(repo)

    @pytest.mark.asyncio
    async def test_get_common_place_success(self, service, repo):
        user_id = uuid4()
        place_id = uuid4()
        mock_place = MagicMock()
        repo.get_by_id.return_value = mock_place

        result = await service.get_common_place(user_id, place_id)

        assert result == mock_place
        repo.get_by_id.assert_called_once_with(user_id, place_id)

    @pytest.mark.asyncio
    async def test_get_common_place_not_found(self, service, repo):
        user_id = uuid4()
        place_id = uuid4()
        repo.get_by_id.return_value = None

        with pytest.raises(CommonPlaceNotFoundError):
            await service.get_common_place(user_id, place_id)


class TestCommonPlaceServiceUpdate:

    @pytest.fixture
    def repo(self):
        return AsyncMock(spec=CommonPlaceRepo)

    @pytest.fixture
    def service(self, repo):
        return CommonPlaceService(repo)

    @pytest.fixture
    def mock_place(self):
        place = MagicMock(spec=CommonPlace)
        place.id = uuid4()
        place.name = "Old Name"
        place.address = "old_encrypted_address"
        return place

    @pytest.mark.asyncio
    async def test_update_common_place_success(self, service, repo, mock_place):
        user_id = uuid4()
        place_id = uuid4()
        dto = CommonPlaceUpdate(name="New Name", address="New Address")
        
        repo.get_by_id.return_value = mock_place
        repo.get_by_user_and_commonplace_name.return_value = None
        repo.update.return_value = mock_place

        with patch("app.modules.common_places.service.encrypt_address", return_value="new_encrypted_address"):
            result = await service.update_common_place(user_id, place_id, dto)

        assert result == mock_place
        assert mock_place.name == "New Name"
        assert mock_place.address == "new_encrypted_address"
        repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_common_place_duplicate_name(self, service, repo, mock_place):
        user_id = uuid4()
        place_id = uuid4()
        dto = CommonPlaceUpdate(name="Existing Name")
        
        repo.get_by_id.return_value = mock_place
        repo.get_by_user_and_commonplace_name.return_value = MagicMock()

        with pytest.raises(DuplicateCommonPlaceError):
            await service.update_common_place(user_id, place_id, dto)

    @pytest.mark.asyncio
    async def test_update_common_place_not_found(self, service, repo):
        user_id = uuid4()
        place_id = uuid4()
        dto = CommonPlaceUpdate(name="New Name")
        repo.get_by_id.return_value = None

        with pytest.raises(CommonPlaceNotFoundError):
            await service.update_common_place(user_id, place_id, dto)


class TestCommonPlaceServiceDelete:

    @pytest.fixture
    def repo(self):
        return AsyncMock(spec=CommonPlaceRepo)

    @pytest.fixture
    def service(self, repo):
        return CommonPlaceService(repo)

    @pytest.mark.asyncio
    async def test_delete_common_place_success(self, service, repo):
        user_id = uuid4()
        place_id = uuid4()
        mock_place = MagicMock()
        repo.get_by_id.return_value = mock_place

        await service.delete_common_place(user_id, place_id)

        repo.delete.assert_called_once_with(mock_place)

    @pytest.mark.asyncio
    async def test_delete_common_place_not_found(self, service, repo):
        user_id = uuid4()
        place_id = uuid4()
        repo.get_by_id.return_value = None

        with pytest.raises(CommonPlaceNotFoundError):
            await service.delete_common_place(user_id, place_id)
