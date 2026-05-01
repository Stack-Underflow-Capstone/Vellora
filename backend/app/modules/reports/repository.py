from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timedelta, timezone
import sqlalchemy as sa
from app.modules.reports.models import Report, ReportStatus
from sqlalchemy.orm import selectinload


class ReportRepository:

    async def create(self, session: AsyncSession, report: Report) -> Report:
        session.add(report)
        await session.flush()
        return report

    async def get_by_id(self, session: AsyncSession, report_id: UUID) -> Report | None:
        result = await session.execute(
            sa.select(Report).where(Report.id == report_id)
            .options(selectinload(Report.user))
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, session: AsyncSession, user_id: UUID) -> list[Report]:
        result = await session.execute(
            sa.select(Report).where(Report.user_id == user_id)
        )
        return list(result.scalars().all())

    async def update(self, session: AsyncSession, report: Report) -> Report:
        await session.flush()
        return report

    async def delete(self, session: AsyncSession, report_id: UUID) -> None:
        result = await session.execute(
            sa.select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        if report:
            await session.delete(report)

    async def get_stuck_reports(self, session: AsyncSession, timeout_minutes: int = 30) -> list[Report]:
        timeout_threshold = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
        
        result = await session.execute(
            sa.select(Report)
            .where(Report.status == ReportStatus.processing)
            .where(Report.processing_started_at < timeout_threshold)
        )
        return list(result.scalars().all())