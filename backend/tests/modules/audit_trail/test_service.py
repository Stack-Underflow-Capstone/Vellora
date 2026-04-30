import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.modules.audit_trail.service import AuditTrailService
from app.modules.audit_trail.repository import AuditTrailRepo
from app.modules.audit_trail.models import AuditAction, AuditTrail
from app.modules.audit_trail.schemas import CreateAuditTrailDTO, EditAuditTrailDTO
from app.modules.audit_trail.exceptions import AuditTrailNotFoundError


class TestAuditTrailService:

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def audit_trail_repo(self):
        return AsyncMock(spec=AuditTrailRepo)

    @pytest.fixture
    def service(self, audit_trail_repo):
        return AuditTrailService(audit_trail_repo)

    @pytest.fixture
    def mock_audit_trail(self):
        audit_trail = MagicMock(spec=AuditTrail)
        audit_trail.id = uuid4()
        audit_trail.user_id = uuid4()
        audit_trail.action = AuditAction.TRIP_STARTED
        audit_trail.resource = "trip"
        audit_trail.resource_id = str(uuid4())
        audit_trail.details = "Test trip started"
        audit_trail.success = True
        audit_trail.error_message = None
        return audit_trail

    @pytest.mark.asyncio
    async def test_create_audit_trail_success(self, service, audit_trail_repo, user_id, mock_audit_trail):
        audit_trail_repo.save.return_value = mock_audit_trail
        
        data = CreateAuditTrailDTO(
            user_id=user_id,
            action=AuditAction.TRIP_STARTED,
            resource="trip",
            resource_id="trip-123",
            details="Started trip to downtown",
            success=True
        )
        
        # Mock the save to return the mock without creating the real object
        result = await service.create_audit_trail(data)
        
        audit_trail_repo.save.assert_called_once()
        assert result == mock_audit_trail

    @pytest.mark.asyncio
    async def test_log_action_success(self, service, audit_trail_repo, user_id, mock_audit_trail):
        audit_trail_repo.save.return_value = mock_audit_trail
        
        result = await service.log_action(
            user_id=user_id,
            action=AuditAction.TRIP_COMPLETED,
            resource="trip",
            resource_id="trip-456",
            details="Trip completed successfully"
        )
        
        audit_trail_repo.save.assert_called_once()
        assert result == mock_audit_trail

    @pytest.mark.asyncio
    async def test_get_audit_trail_found(self, service, audit_trail_repo, mock_audit_trail):
        audit_trail_repo.get_audit_trail.return_value = mock_audit_trail
        
        result = await service.get_audit_trail(mock_audit_trail.id)
        
        audit_trail_repo.get_audit_trail.assert_called_once_with(mock_audit_trail.id, None)
        assert result == mock_audit_trail

    @pytest.mark.asyncio
    async def test_get_audit_trail_not_found(self, service, audit_trail_repo):
        audit_trail_repo.get_audit_trail.return_value = None
        
        with pytest.raises(AuditTrailNotFoundError, match="Audit trail not found"):
            await service.get_audit_trail(uuid4())

    @pytest.mark.asyncio
    async def test_get_user_audit_history(self, service, audit_trail_repo, user_id):
        expected_trails = [MagicMock(), MagicMock()]
        audit_trail_repo.get_audit_trails_by_user_id.return_value = expected_trails
        
        result = await service.get_user_audit_history(user_id)
        
        audit_trail_repo.get_audit_trails_by_user_id.assert_called_once_with(user_id)
        assert result == expected_trails

    @pytest.mark.asyncio
    async def test_get_resource_audit_history(self, service, audit_trail_repo):
        expected_trails = [MagicMock()]
        audit_trail_repo.get_audit_trails_by_resource.return_value = expected_trails
        
        result = await service.get_resource_audit_history("trip", "trip-789")
        
        audit_trail_repo.get_audit_trails_by_resource.assert_called_once_with("trip", "trip-789")
        assert result == expected_trails