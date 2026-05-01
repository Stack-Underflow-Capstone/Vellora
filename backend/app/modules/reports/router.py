from datetime import datetime, timezone
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter

from app.container import get_db
from app.modules.reports.repository import ReportRepository
from app.modules.reports.service import ReportsService
from app.modules.reports.schemas import GenerateReportDTO, ReportResponse, ReportStatusResponse, AnalyticsResponse
from app.core.dependencies import get_current_user
from app.modules.reports.models import ReportStatus
from app.modules.reports.data_builder import ReportDataBuilder
from app.modules.reports.renderer_fpdf import ReportPDFRenderer
from app.infra.adapters.s3_report_storage_adapter import S3ReportStorageAdapter
from app.infra.adapters.sqs_report_queue_adapter import SQSReportQueueAdapter
from app.infra.adapters.email_notification_adapter import EmailNotificationAdapter
from app.modules.audit_trail.service import AuditTrailService
from app.core.error_handler import error_handler


router = APIRouter(prefix="/reports", tags=["Reports"])

def get_reports_service(db: AsyncSession = Depends(get_db)):
    repo = ReportRepository()
    data_builder = ReportDataBuilder(db)
    renderer = ReportPDFRenderer()
    storage = S3ReportStorageAdapter()
    queue = SQSReportQueueAdapter()
    notification_service = EmailNotificationAdapter()
    from app.modules.audit_trail.repository import AuditTrailRepo
    audit_service = AuditTrailService(AuditTrailRepo(db))
    return ReportsService(db, repo, data_builder, renderer, storage, queue, notification_service, audit_service)

@router.get("/analytics/{month}", response_model=AnalyticsResponse)
@error_handler
async def get_analytics(month: str, user=Depends(get_current_user), service: ReportsService = Depends(get_reports_service)):
    analytics = await service.get_analytics(user, month)
    return AnalyticsResponse.model_validate(analytics, from_attributes=True)

@router.post("", response_model=ReportResponse)
@error_handler
async def create_report(dto: GenerateReportDTO, user=Depends(get_current_user), service: ReportsService = Depends(get_reports_service)):
    report = await service.generate_report(user.id, dto)
    return ReportResponse.model_validate(report, from_attributes=True)


#for frontend u might need to poll like every 3 secs or smthn so that the status get updated
@router.get("/{report_id}/status", response_model=ReportStatusResponse)
@error_handler
async def check_report_status(report_id: UUID, service: ReportsService = Depends(get_reports_service)):
    report = await service.get_report_status(report_id)
    return ReportStatusResponse(
        id=report.id,
        status=report.status,
        file_url=report.file_url
    )

@router.get("/{report_id}/download")
@error_handler
async def download_report(report_id: UUID, user=Depends(get_current_user), service: ReportsService = Depends(get_reports_service)):
    download_url = await service.get_download_url(report_id, user.id)
    return {"download_url": download_url}

@router.get("/history", response_model=list[ReportResponse])
@error_handler
async def list_reports(user=Depends(get_current_user), service: ReportsService = Depends(get_reports_service)):
    reports = await service.list_user_reports(user.id)
    return [
        ReportResponse.model_validate(r, from_attributes=True)
        for r in reports
    ]

@router.post("/{report_id}/retry", response_model=ReportResponse)
@error_handler
async def retry_report(report_id: UUID, service: ReportsService = Depends(get_reports_service), user=Depends(get_current_user)):
    report = await service.retry_report(report_id, user.id)
    return ReportResponse.model_validate(report, from_attributes=True)


@router.post("/{report_id}/regenerate")
@error_handler
async def regenerate_report(report_id: UUID,service: ReportsService = Depends(get_reports_service), user=Depends(get_current_user)):
    result = await service.regenerate_report(report_id, user.id)
    return result

@router.delete("/{report_id}")
@error_handler
async def delete_report(report_id: UUID, user=Depends(get_current_user), service: ReportsService = Depends(get_reports_service)):
    await service.delete_report(report_id, user.id)
    return {"message": "Report deleted successfully"}