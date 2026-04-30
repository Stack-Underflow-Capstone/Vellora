from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.audit_trail.models import AuditTrail, AuditAction


class AuditTrailRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, audit_trail: AuditTrail) -> AuditTrail:
        self.db.add(audit_trail)
        await self.db.commit()
        await self.db.refresh(audit_trail)
        return audit_trail
    
    async def get_audit_trail(self, audit_id: UUID, user_id: UUID = None) -> AuditTrail:
        query = select(AuditTrail).where(AuditTrail.id == audit_id)
        if user_id is not None:
            query = query.where(AuditTrail.user_id == user_id)
        return await self.db.scalar(query)
    
    async def get_audit_trails_by_user_id(self, user_id: UUID):
        query = select(AuditTrail).where(AuditTrail.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_audit_trails_by_resource(self, resource: str, resource_id: str = None):
        query = select(AuditTrail).where(AuditTrail.resource == resource)
        if resource_id is not None:
            query = query.where(AuditTrail.resource_id == resource_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def delete_audit_trail(self, audit_trail: AuditTrail) -> None:       
        await self.db.delete(audit_trail)
        await self.db.commit()