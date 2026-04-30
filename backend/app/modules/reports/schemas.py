from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, field_validator

from app.modules.reports.models import ReportStatus


class GenerateReportDTO(BaseModel):
    start_date: date
    end_date: date

    @field_validator("end_date")
    def validate_dates(cls, end_value, info):
        start_value = info.data.get("start_date")

        if start_value and end_value < start_value:
            raise ValueError("end_date cannot be earlier than start_date")

        return end_value


class ReportResponse(BaseModel):
    id: UUID
    user_id: UUID
    start_date: date
    end_date: date
    status: str
    file_name: str | None
    file_url: str | None
    requested_at: datetime
    completed_at: datetime | None
    expires_at: datetime | None


    class Config:
        from_attributes = True


class ReportStatusResponse(BaseModel):
    id: UUID
    status: ReportStatus
    file_url: str | None

class AnalyticsResponse(BaseModel):
    category_counts: dict[str, int]
    total_miles: float
    grand_total: float