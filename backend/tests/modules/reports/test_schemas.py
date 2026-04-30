import pytest
from datetime import date, datetime
from uuid import uuid4
from pydantic import ValidationError

from app.modules.reports.schemas import GenerateReportDTO, ReportResponse, ReportStatusResponse, AnalyticsResponse
from app.modules.reports.models import ReportStatus


class TestGenerateReportDTO:

    def test_valid_date_range(self):
        dto = GenerateReportDTO(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        assert dto.start_date == date(2024, 1, 1)
        assert dto.end_date == date(2024, 1, 31)

    def test_same_start_end_date(self):
        dto = GenerateReportDTO(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )
        assert dto.start_date == dto.end_date

    def test_end_date_before_start_date_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            GenerateReportDTO(
                start_date=date(2024, 1, 31),
                end_date=date(2024, 1, 1)
            )
        assert "end_date cannot be earlier than start_date" in str(exc_info.value)


class TestReportResponse:

    def test_valid_response_creation(self):
        response = ReportResponse(
            id=uuid4(),
            user_id=uuid4(),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            status="pending",
            file_name=None,
            file_url=None,
            requested_at=datetime.now(),
            completed_at=None,
            expires_at=None
        )
        assert response.status == "pending"
        assert response.file_name is None


class TestReportStatusResponse:

    def test_valid_status_response(self):
        response = ReportStatusResponse(
            id=uuid4(),
            status=ReportStatus.pending,
            file_url=None
        )
        assert response.status == ReportStatus.pending
        assert response.file_url is None


class TestAnalyticsResponse:

    def test_valid_analytics_response(self):
        response = AnalyticsResponse(
            category_counts={"Business": 5, "Personal": 3},
            total_miles=250.5,
            grand_total=158.75
        )
        assert response.category_counts == {"Business": 5, "Personal": 3}
        assert response.total_miles == 250.5
        assert response.grand_total == 158.75

    def test_invalid_analytics_response_missing_fields(self):
        with pytest.raises(ValidationError):
            AnalyticsResponse(category_counts={"Business": 5})

    def test_category_counts_is_dict(self):
        response = AnalyticsResponse(
            category_counts={"Work": 10},
            total_miles=100.0,
            grand_total=65.0
        )
        assert isinstance(response.category_counts, dict)

    def test_integers_converted_to_floats(self):
        response = AnalyticsResponse(
            category_counts={"Work": 10},
            total_miles=100,
            grand_total=65
        )
        assert response.total_miles == 100.0
        assert response.grand_total == 65.0