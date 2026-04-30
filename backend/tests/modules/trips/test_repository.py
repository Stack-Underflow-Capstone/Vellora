import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.modules.trips.repository import TripRepo
from app.modules.trips.models import TripStatus


class TestTripRepoDesignDiscussion:

    @pytest.fixture
    def repo(self, mock_db_session):
        return TripRepo(mock_db_session)

 #Cant test this due to tight coupling so will instead test it using integration testing

