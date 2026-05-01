import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import json

from app.worker import ReportWorker
from app.modules.reports.models import Report, ReportStatus


class TestReportWorker:

    @pytest.fixture
    def mock_sqs_client(self):
        sqs = MagicMock()
        sqs.get_queue_url.return_value = {"QueueUrl": "test-queue-url"}
        return sqs

    @pytest.fixture
    def worker(self, mock_sqs_client):
        with patch('app.worker.get_sqs_client', return_value=mock_sqs_client):
            return ReportWorker()

    @pytest.fixture
    def sample_message(self):
        return {
            "Body": json.dumps({"report_id": str(uuid4())}),
            "ReceiptHandle": "test-receipt-handle",
            "Attributes": {
                "ApproximateReceiveCount": "1"
            }
        }

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def mock_report(self):
        report = MagicMock(spec=Report)
        report.id = uuid4()
        report.status = ReportStatus.pending
        report.file_name = "test-report.pdf"
        return report

    @patch('app.worker.AsyncSessionLocal')
    async def test_process_report_success(
        self, mock_session_local, worker, mock_session, mock_report
    ):
        mock_session_local.return_value.__aenter__.return_value = mock_session
        
        with patch('app.worker.ReportRepository') as mock_repo_class, \
             patch('app.worker.ReportsService') as mock_service_class, \
             patch('app.worker.S3ReportStorageAdapter'), \
             patch('app.worker.SQSReportQueueAdapter'), \
             patch('app.worker.EmailNotificationAdapter'):
            
            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = mock_report
            mock_repo_class.return_value = mock_repo
            
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            # Mock the SQS client delete_message method
            worker.sqs.delete_message = MagicMock()
            
            result = await worker.process_report(str(mock_report.id), "test-receipt-handle")
            
            assert result is True
            mock_repo.get_by_id.assert_called()
            mock_service.mark_processing_started.assert_called_once_with(str(mock_report.id))
            mock_service.generate_now.assert_called_once_with(str(mock_report.id))

    @patch('app.worker.AsyncSessionLocal')
    async def test_process_report_not_found(
        self, mock_session_local, worker, mock_session
    ):
        mock_session_local.return_value.__aenter__.return_value = mock_session
        
        with patch('app.worker.ReportRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = None
            mock_repo_class.return_value = mock_repo
            
            # Mock the SQS client delete_message method
            worker.sqs.delete_message = MagicMock()
            
            result = await worker.process_report(str(uuid4()), "test-receipt-handle")
            
            assert result is True  # Skip non-existent reports

    @patch('app.worker.AsyncSessionLocal')
    async def test_process_report_already_completed(
        self, mock_session_local, worker, mock_session, mock_report
    ):
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_report.status = ReportStatus.completed
        
        with patch('app.worker.ReportRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = mock_report
            mock_repo_class.return_value = mock_repo
            
            # Mock the SQS client delete_message method
            worker.sqs.delete_message = MagicMock()
            
            result = await worker.process_report(str(mock_report.id), "test-receipt-handle")
            
            assert result is True  # Skip completed reports

    @patch('app.worker.AsyncSessionLocal')
    async def test_process_report_service_error(
        self, mock_session_local, worker, mock_session, mock_report
    ):
        mock_session_local.return_value.__aenter__.return_value = mock_session
        
        with patch('app.worker.ReportRepository') as mock_repo_class, \
             patch('app.worker.ReportsService') as mock_service_class, \
             patch('app.worker.S3ReportStorageAdapter'), \
             patch('app.worker.SQSReportQueueAdapter'), \
             patch('app.worker.EmailNotificationAdapter'):
            
            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = mock_report
            mock_repo_class.return_value = mock_repo
            
            mock_service = AsyncMock()
            mock_service.mark_processing_started.side_effect = Exception("Service error")
            mock_service_class.return_value = mock_service
            
            # Mock the SQS client delete_message method
            worker.sqs.delete_message = MagicMock()
            
            # Mock the mark_failed method to return True
            with patch.object(worker, 'mark_failed', return_value=True) as mock_mark_failed:
                result = await worker.process_report(str(mock_report.id), "test-receipt-handle")
                
                # Since mark_failed succeeds, the message gets deleted and returns True
                assert result is True
                mock_mark_failed.assert_called()

    async def test_mark_failed(self, worker, mock_session, mock_report):
        with patch('app.worker.ReportRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = mock_report
            mock_repo_class.return_value = mock_repo
            
            result = await worker.mark_failed(mock_session, str(mock_report.id))
            
            assert result is True
            assert mock_report.status == ReportStatus.failed
            mock_session.commit.assert_called_once()

    async def test_mark_failed_not_found(self, worker, mock_session):
        with patch('app.worker.ReportRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = None
            mock_repo_class.return_value = mock_repo
            
            result = await worker.mark_failed(mock_session, str(uuid4()))
            
            assert result is False
            # Should not commit if report not found
            mock_session.commit.assert_not_called()