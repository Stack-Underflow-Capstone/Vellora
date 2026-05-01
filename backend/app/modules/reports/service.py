from datetime import date,datetime, timedelta, timezone
from calendar import monthrange
from collections import Counter
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from app.modules.reports.schemas import GenerateReportDTO, AnalyticsResponse
from app.modules.reports.models import Report, ReportStatus
from app.modules.reports.repository import ReportRepository
from app.modules.reports.data_builder import ReportDataBuilder
from app.modules.reports.renderer_fpdf import ReportPDFRenderer
from app.modules.reports.exceptions import (
    ReportNotFoundError, ReportPermissionError, ReportRateLimitError,
    ReportSystemLimitError, ReportMaxRetriesError, ReportInvalidStateError,
    ReportExpiredError, ReportPersistenceError, InvalidMonthAnalyticsError,
    InvalidDataAnalyticsError
)
from app.modules.reports.ports import NotificationPort, StoragePort, QueuePort
from app.modules.users.models import User
from app.modules.audit_trail.service import AuditTrailService
from app.modules.audit_trail.models import AuditAction
import logging


class ReportsService:
    SYSTEM_MAX = 50
    MAX_RETRY_ATTEMPTS = 3

    def __init__(self, session: AsyncSession, repo: ReportRepository, data_builder: ReportDataBuilder | None = None, renderer: ReportPDFRenderer | None = None, storage: StoragePort | None = None, queue: QueuePort | None = None, notification_service: NotificationPort | None = None, audit_service: AuditTrailService | None = None):
        self.session = session
        self.repo = repo
        self.data_builder = data_builder or ReportDataBuilder(session)
        self.renderer = renderer or ReportPDFRenderer()
        
        if storage is None:
            raise ValueError("Storage port is required")
        if queue is None:
            raise ValueError("Queue port is required")
            
        self.storage = storage
        self.queue = queue
        self.notification_service = notification_service
        self.audit_service = audit_service or AuditTrailService(session)

    async def generate_report(self, user_id: UUID, dto: GenerateReportDTO) -> Report:
        #rate limit stuff. disable when in local dev
        await self.validate_global_limit()
        await self.validate_rate_limit(user_id)
        report = Report(
            user_id=user_id,
            start_date=dto.start_date,
            end_date=dto.end_date,
            status=ReportStatus.pending,
        )

        try:
            created_report = await self.repo.create(self.session, report)
            await self.session.commit()
            
            #log audit trail
            await self.audit_service.log_report_requested(
                user_id=user_id,
                report_id=str(created_report.id),
                details=f"Report requested for date range {dto.start_date} to {dto.end_date}"
            )
            
            self.queue.send(str(created_report.id))
            
            return created_report
        except Exception as e:
            await self.session.rollback()
            raise ReportPersistenceError("Failed to create report") from e

    async def generate_now(self, report_id: UUID) -> Report:
        report = await self.repo.get_by_id(self.session, report_id)
        if not report:
            raise ReportNotFoundError("Report not found")

        data = await self.data_builder.build(report)

        pdf_bytes = self.renderer.render(data)

        key = self.storage.save(report.id, pdf_bytes)

        report.file_name = key
        report.file_url = key
        report.status = ReportStatus.completed
        now = datetime.now(timezone.utc)
        report.completed_at = now
        report.expires_at = now + timedelta(days=90)

        await self.session.commit()
        await self.session.refresh(report)
        
        #log audit trail
        await self.audit_service.log_report_generated(
            user_id=report.user_id,
            report_id=str(report.id),
            details=f"Report generated successfully with file key: {key}"
        )

        if self.notification_service:
            try:
                user_result = await self.session.get(User, report.user_id)
                if user_result:
                    download_url = self.storage.get_signed_url(report.file_name)
                    await self.notification_service.notify_report_completed(
                        user=user_result,
                        report=report,
                        download_url=download_url
                    )
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to send notification for report {report.id}: {str(e)}")

        return report
    
    async def retry_report(self, report_id: UUID, user_id: UUID) -> Report:
        #rate limiting. disable in local dev
        await self.validate_global_limit()
        
        report = await self.repo.get_by_id(self.session, report_id)

        if not report:
            raise ReportNotFoundError("Report not found")

        if report.user_id != user_id:
            raise ReportPermissionError("Not allowed to retry this report")

        if report.status not in {ReportStatus.failed, ReportStatus.expired}:
            raise ReportInvalidStateError("Only failed or expired reports can be retried")
        
        #rate limiting. disable in local dev
        if report.retry_attempts >= self.MAX_RETRY_ATTEMPTS:
            raise ReportMaxRetriesError("Maximum retry attempts reached for this report")

        report.retry_attempts += 1

        #reset state
        report.status = ReportStatus.pending
        report.file_url = None
        report.file_name = None
        report.expires_at = None
        report.completed_at = None

        try:
            await self.repo.update(self.session, report)
            await self.session.commit()

            #requeue
            self.queue.send(str(report.id))

            return report
        except Exception as e:
            await self.session.rollback()
            raise ReportPersistenceError("Failed to retry report") from e
    
    async def regenerate_report(self, report_id: UUID, user_id: UUID):
        
        #rate limiting. disable in local dev
        await self.validate_global_limit()

        report = await self.repo.get_by_id(self.session, report_id)

        if not report:
            raise ReportNotFoundError("Report not found")

        if report.user_id != user_id:
            raise ReportPermissionError("Not allowed to regenerate this report")

        if report.status not in {ReportStatus.completed, ReportStatus.expired}:
            raise ReportInvalidStateError("Only completed or expired reports can be regenerated")
        
        #rate limiting. disable in local dev
        if report.retry_attempts >= self.MAX_RETRY_ATTEMPTS:
            raise ReportMaxRetriesError("Maximum attempts reached for this report")

        #if file still exists in storage then try to sign it
        if report.file_name:
            if self.storage.exists(report.file_name):
                now = datetime.now(timezone.utc)
                report.expires_at = now + timedelta(days=90)
                await self.session.commit()
                
                url = self.storage.get_signed_url(report.file_name)
                return {
                    "status": "available",
                    "download_url": url
                }

        try:
            #if file missing then regenerate
            report.status = ReportStatus.pending
            report.file_url = None
            report.file_name = None
            report.expires_at = None
            report.completed_at = None
            report.retry_attempts += 1

            await self.repo.update(self.session, report)
            await self.session.commit()

            self.queue.send(str(report.id))

            return {"status": "regenerating"}
        except Exception as e:
            await self.session.rollback()
            raise ReportPersistenceError("Failed to regenerate report") from e
    
    async def validate_rate_limit(self, user_id: UUID):
        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        recent_count = await self.session.scalar(
            select(func.count(Report.id))
            .where(Report.user_id == user_id)
            .where(Report.requested_at > one_minute_ago)
        )

        daily_count = await self.session.scalar(
            select(func.count(Report.id))
            .where(Report.user_id == user_id)
            .where(Report.requested_at > today_start)
        )

        if recent_count >= 1:
            raise ReportRateLimitError("Too many requests please try again in a minute")

        if daily_count >= 5:
            raise ReportRateLimitError("Daily report limit reached")
        
    async def validate_global_limit(self):
        pending_count = await self.session.scalar(
            sa.select(sa.func.count(Report.id)).where(
                Report.status.in_([ReportStatus.pending, ReportStatus.processing])
            )
        )

        if pending_count >= self.SYSTEM_MAX:
            raise ReportSystemLimitError("System busy please try again later.")

    async def get_report_status(self, report_id: UUID) -> Report:
        report = await self.repo.get_by_id(self.session, report_id)
        if not report:
            raise ReportNotFoundError("Report not found")
        return report

    async def get_download_url(self, report_id: UUID, user_id: UUID) -> str:
        report = await self.repo.get_by_id(self.session, report_id)
        
        if not report:
            raise ReportNotFoundError("Report not found")
            
        if report.user_id != user_id:
            raise ReportPermissionError("Not allowed to access this report")
        
        # Check if expired
        now = datetime.now(timezone.utc)
        if report.expires_at and report.expires_at < now:
            report.status = ReportStatus.expired
            await self.session.commit()
            raise ReportExpiredError("Report expired please regenerate")

        if report.status != ReportStatus.completed:
            raise ReportInvalidStateError("Report not generated yet")

        #check if file still exists in storage
        if not self.storage.exists(report.file_name):
            report.status = ReportStatus.expired
            await self.session.commit()
            raise ReportExpiredError("Report no longer available and must be regenerated")

        #log audit trail
        await self.audit_service.log_report_downloaded(
            user_id=user_id,
            report_id=str(report.id),
            details=f"Report download URL generated for file: {report.file_name}"
        )

        return self.storage.get_signed_url(report.file_name)

    async def list_user_reports(self, user_id: UUID) -> list[Report]:
        reports = await self.repo.list_for_user(self.session, user_id)
        reports.sort(key=lambda r: r.requested_at, reverse=True)
        
        now = datetime.now(timezone.utc)
        changed = False
        
        for report in reports:
            if (report.status == ReportStatus.completed 
                and report.expires_at 
                and report.expires_at < now):
                report.status = ReportStatus.expired
                changed = True

        if changed:
            await self.session.commit()

        return reports

    async def delete_report(self, report_id: UUID, user_id: UUID) -> None:
        report = await self.repo.get_by_id(self.session, report_id)
        
        if not report:
            raise ReportNotFoundError("Report not found")
            
        if report.user_id != user_id:
            raise ReportPermissionError("Not allowed to delete this report")
        
        if report.file_name and self.storage.exists(report.file_name):
            try:
                self.storage.delete(report.file_name)
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to delete file {report.file_name} from storage: {str(e)}")
        
        try:
            await self.repo.delete(self.session, report_id)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise ReportPersistenceError("Failed to delete report") from e

    async def cleanup_stuck_reports(self, timeout_minutes: int = 30) -> int:

        #if its been longer than 30 mins consider it stuck.
        stuck_reports = await self.repo.get_stuck_reports(self.session, timeout_minutes)
        
        count = 0
        for report in stuck_reports:
            report.status = ReportStatus.failed
            count += 1
            
            #log audit trail
            await self.audit_service.log_report_failed(
                user_id=report.user_id,
                report_id=str(report.id),
                error_message="Report generation timed out",
                details=f"Report was stuck in processing for over {timeout_minutes} minutes"
            )
            
            if self.notification_service:
                try:
                    user = await self.session.get(User, report.user_id)
                    if user:
                        await self.notification_service.notify_report_failed(user, report)
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to send notification for stuck report {report.id}: {str(e)}")
        
        if count > 0:
            await self.session.commit()
            logger = logging.getLogger(__name__)
            logger.info(f"Cleaned up {count} stuck reports")
        
        return count

    async def mark_processing_started(self, report_id: UUID) -> None:
        report = await self.repo.get_by_id(self.session, report_id)
        if report:
            report.status = ReportStatus.processing
            report.processing_started_at = datetime.now(timezone.utc)
            await self.session.commit()

    async def get_analytics(self, user: User, month: str) -> AnalyticsResponse:
        #Gets the analytics for a user for a specific month
        year = date.today().year
        current_month = date.today().month

        try:
            month_num = datetime.strptime(month.capitalize(), "%B").month
        except ValueError:
            raise InvalidMonthAnalyticsError("Invalid Month")

        start_date = date(year, month_num, 1)
        end_date = date(year, month_num, monthrange(year, month_num)[1])

        try:
            temp_report = Report(
            user = user,
            user_id=user.id,
            start_date=start_date,
            end_date=end_date
        )
            data = await self.data_builder.build(temp_report)
        except Exception as e:
            raise InvalidDataAnalyticsError("Failed to gather data") from e

        category_counts = Counter(trip.category_name for trip in data.trips)
        
        return AnalyticsResponse(
            category_counts=dict(category_counts),
            total_miles=data.total_miles,
            grand_total=data.grand_total
        )