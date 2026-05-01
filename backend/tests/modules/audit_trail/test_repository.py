import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from app.modules.audit_trail.repository import AuditTrailRepo
from app.modules.audit_trail.models import AuditTrail, AuditAction


class TestAuditTrailRepo:

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.execute = AsyncMock()
        db.scalar = AsyncMock()
        db.delete = AsyncMock()
        return db

    @pytest.fixture
    def repository(self, mock_db):
        return AuditTrailRepo(mock_db)

    @pytest.fixture
    def mock_audit_trail(self):
        audit_trail = MagicMock(spec=AuditTrail)
        audit_trail.id = uuid4()
        audit_trail.user_id = uuid4()
        audit_trail.action = AuditAction.TRIP_STARTED
        audit_trail.resource = "trip"
        audit_trail.resource_id = str(uuid4())
        return audit_trail

    @pytest.mark.asyncio
    async def test_save_audit_trail(self, repository, mock_db, mock_audit_trail):
        result = await repository.save(mock_audit_trail)
        
        mock_db.add.assert_called_once_with(mock_audit_trail)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_audit_trail)
        assert result == mock_audit_trail

    @pytest.mark.asyncio
    async def test_get_audit_trail_found(self, repository, mock_db, mock_audit_trail):
        mock_db.scalar.return_value = mock_audit_trail
        
        result = await repository.get_audit_trail(mock_audit_trail.id)
        
        mock_db.scalar.assert_called_once()
        assert result == mock_audit_trail

    @pytest.mark.asyncio
    async def test_get_audit_trail_not_found(self, repository, mock_db):
        mock_db.scalar.return_value = None
        
        result = await repository.get_audit_trail(uuid4())
        
        mock_db.scalar.assert_called_once()
        assert result is None

    @pytest.mark.asyncio
    async def test_get_audit_trail_with_user_filter(self, repository, mock_db, mock_audit_trail):
        user_id = uuid4()
        mock_db.scalar.return_value = mock_audit_trail
        
        result = await repository.get_audit_trail(mock_audit_trail.id, user_id)
        
        mock_db.scalar.assert_called_once()
        assert result == mock_audit_trail

    @pytest.mark.asyncio
    async def test_get_audit_trails_by_user_id(self, repository, mock_db):
        user_id = uuid4()
        expected_trails = [MagicMock(), MagicMock()]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = expected_trails
        mock_db.execute.return_value = mock_result
        
        result = await repository.get_audit_trails_by_user_id(user_id)
        
        mock_db.execute.assert_called_once()
        assert result == expected_trails

    @pytest.mark.asyncio
    async def test_get_audit_trails_by_resource(self, repository, mock_db):
        expected_trails = [MagicMock()]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = expected_trails
        mock_db.execute.return_value = mock_result
        
        result = await repository.get_audit_trails_by_resource("trip", "trip-123")
        
        mock_db.execute.assert_called_once()
        assert result == expected_trails

    @pytest.mark.asyncio
    async def test_get_audit_trails_by_resource_no_resource_id(self, repository, mock_db):
        expected_trails = [MagicMock()]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = expected_trails
        mock_db.execute.return_value = mock_result
        
        result = await repository.get_audit_trails_by_resource("trip")
        
        mock_db.execute.assert_called_once()
        assert result == expected_trails

    @pytest.mark.asyncio
    async def test_delete_audit_trail(self, repository, mock_db, mock_audit_trail):
        await repository.delete_audit_trail(mock_audit_trail)
        
        mock_db.delete.assert_called_once_with(mock_audit_trail)
        mock_db.commit.assert_called_once()