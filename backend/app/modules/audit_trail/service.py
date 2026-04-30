from uuid import UUID
from app.modules.audit_trail.repository import AuditTrailRepo
from app.modules.audit_trail.schemas import CreateAuditTrailDTO, EditAuditTrailDTO
from app.modules.audit_trail.models import AuditTrail, AuditAction
from app.modules.audit_trail.exceptions import AuditTrailNotFoundError


class AuditTrailService:
    def __init__(self, audit_trail_repo: AuditTrailRepo):
        self.audit_trail_repo = audit_trail_repo

    async def create_audit_trail(self, data: CreateAuditTrailDTO):
        audit_trail = AuditTrail(
            user_id=data.user_id,
            action=data.action,
            resource=data.resource,
            resource_id=data.resource_id,
            details=data.details,
            success=data.success,
            error_message=data.error_message
        )
        
        return await self.audit_trail_repo.save(audit_trail)

    async def log_action(self, user_id: UUID, action: AuditAction, resource: str, resource_id: str = None, details: str = None, success: bool = True, error_message: str = None):
        data = CreateAuditTrailDTO(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
            success=success,
            error_message=error_message
        )
        
        return await self.create_audit_trail(data)
    
    async def get_audit_trail(self, audit_id: UUID, user_id: UUID = None):
        audit_trail = await self.audit_trail_repo.get_audit_trail(audit_id, user_id)
        if not audit_trail:
            raise AuditTrailNotFoundError("Audit trail not found")
        return audit_trail
    
    async def get_user_audit_history(self, user_id: UUID):
        return await self.audit_trail_repo.get_audit_trails_by_user_id(user_id)
    
    async def get_resource_audit_history(self, resource: str, resource_id: str = None):
        return await self.audit_trail_repo.get_audit_trails_by_resource(resource, resource_id)
    

    async def log_report_requested(self, user_id: UUID, report_id: str, details: str = None):
        return await self.log_action(
            user_id=user_id,
            action=AuditAction.REPORT_REQUESTED,
            resource="report",
            resource_id=report_id,
            details=details
        )
    
    async def log_report_generated(self, user_id: UUID, report_id: str, details: str = None):
        return await self.log_action(
            user_id=user_id,
            action=AuditAction.REPORT_GENERATED,
            resource="report",
            resource_id=report_id,
            details=details
        )
    
    async def log_report_downloaded(self, user_id: UUID, report_id: str, details: str = None):
        return await self.log_action(
            user_id=user_id,
            action=AuditAction.REPORT_DOWNLOADED,
            resource="report",
            resource_id=report_id,
            details=details
        )
    
    async def log_report_failed(self, user_id: UUID, report_id: str, error_message: str, details: str = None):
        return await self.log_action(
            user_id=user_id,
            action=AuditAction.REPORT_FAILED,
            resource="report",
            resource_id=report_id,
            details=details,
            success=False,
            error_message=error_message
        )