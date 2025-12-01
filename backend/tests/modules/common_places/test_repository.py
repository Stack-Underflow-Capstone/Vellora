import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from app.modules.common_places.repository import CommonPlaceRepo
from app.modules.common_places.models import CommonPlace


class TestCommonPlaceRepoCreate:

    @pytest.fixture
    def repo(self, mock_db_session):
        return CommonPlaceRepo(mock_db_session)

    @pytest.fixture
    def mock_place(self):
        place = MagicMock(spec=CommonPlace)
        place.id = uuid4()
        place.user_id = uuid4()
        place.name = "Home"
        place.address = "encrypted_address"
        return place

    @pytest.mark.asyncio
    async def test_create_common_place(self, repo, mock_db_session, mock_place):
        result = await repo.create(mock_place)

        mock_db_session.add.assert_called_once_with(mock_place)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_place)
        assert result == mock_place


class TestCommonPlaceRepoGet:

    @pytest.fixture
    def repo(self, mock_db_session):
        return CommonPlaceRepo(mock_db_session)

    @pytest.fixture
    def mock_place(self):
        place = MagicMock(spec=CommonPlace)
        place.id = uuid4()
        place.user_id = uuid4()
        place.name = "Home"
        return place

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repo, mock_db_session, mock_place):
        place_id = uuid4()
        user_id = uuid4()
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_place
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_id(user_id, place_id)

        assert result == mock_place
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repo, mock_db_session):
        place_id = uuid4()
        user_id = uuid4()
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_id(user_id, place_id)

        assert result is None
        mock_db_session.execute.assert_called_once()


class TestCommonPlaceRepoGetAll:

    @pytest.fixture
    def repo(self, mock_db_session):
        return CommonPlaceRepo(mock_db_session)

    @pytest.fixture
    def mock_places(self):
        places = []
        for i in range(3):
            place = MagicMock(spec=CommonPlace)
            place.id = uuid4()
            place.name = f"Place {i}"
            places.append(place)
        return places

    @pytest.mark.asyncio
    async def test_get_all_by_user_found(self, repo, mock_db_session, mock_places):
        user_id = uuid4()
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_places
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_all_by_user(user_id)

        assert result == mock_places
        assert len(result) == 3
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_by_user_empty(self, repo, mock_db_session):
        user_id = uuid4()
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_all_by_user(user_id)

        assert result == []
        mock_db_session.execute.assert_called_once()


class TestCommonPlaceRepoGetByName:

    @pytest.fixture
    def repo(self, mock_db_session):
        return CommonPlaceRepo(mock_db_session)

    @pytest.fixture
    def mock_place(self):
        place = MagicMock(spec=CommonPlace)
        place.id = uuid4()
        place.name = "Home"
        return place

    @pytest.mark.asyncio
    async def test_get_by_name_found(self, repo, mock_db_session, mock_place):
        user_id = uuid4()
        name = "Home"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_place
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_user_and_commonplace_name(user_id, name)

        assert result == mock_place
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, repo, mock_db_session):
        user_id = uuid4()
        name = "NonExistent"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_user_and_commonplace_name(user_id, name)

        assert result is None
        mock_db_session.execute.assert_called_once()


class TestCommonPlaceRepoUpdate:

    @pytest.fixture
    def repo(self, mock_db_session):
        return CommonPlaceRepo(mock_db_session)

    @pytest.fixture
    def mock_place(self):
        place = MagicMock(spec=CommonPlace)
        place.id = uuid4()
        place.name = "Updated Name"
        return place

    @pytest.mark.asyncio
    async def test_update_common_place(self, repo, mock_db_session, mock_place):
        result = await repo.update(mock_place)

        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_place)
        assert result == mock_place


class TestCommonPlaceRepoDelete:

    @pytest.fixture
    def repo(self, mock_db_session):
        return CommonPlaceRepo(mock_db_session)

    @pytest.fixture
    def mock_place(self):
        place = MagicMock(spec=CommonPlace)
        place.id = uuid4()
        return place

    @pytest.mark.asyncio
    async def test_delete_common_place(self, repo, mock_db_session, mock_place):
        await repo.delete(mock_place)

        mock_db_session.delete.assert_called_once_with(mock_place)
        mock_db_session.commit.assert_called_once()
