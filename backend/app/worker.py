import asyncio
import json

from app.aws_client import get_sqs_client
from app.config import settings
from app.infra.db import AsyncSessionLocal

from app.modules.reports.repository import ReportRepository
from app.modules.reports.service import ReportsService
from app.infra.adapters.email_notification_adapter import EmailNotificationAdapter
from app.infra.adapters.s3_report_storage_adapter import S3ReportStorageAdapter
from app.infra.adapters.sqs_report_queue_adapter import SQSReportQueueAdapter

from app.modules.auth.models import RefreshToken, OAuthAccount
from app.modules.common_places.models import CommonPlace
from app.modules.expenses.models import Expense
from app.modules.rate_categories.models import RateCategory
from app.modules.rate_customizations.models import RateCustomization
from app.modules.reports.models import Report, ReportStatus
from app.modules.trips.models import Trip
from app.modules.users.models import User

VISIBILITY_TIMEOUT = 60 
MAX_RECEIVE_COUNT = 3 

class ReportWorker:

    def __init__(self):
        self.sqs = get_sqs_client()
        self.queue_url = self.sqs.get_queue_url(QueueName=settings.REPORTS_QUEUE)["QueueUrl"]

    async def start(self):
        
        #clean any stuck reports from previous runs
        await self.cleanup_stuck_reports_on_startup()
        
        #start background clean task
        cleanup_task = asyncio.create_task(self.periodic_cleanup())
        
        print("Worker is running and listening for messages...\n")

        try:
            while True:
                response = self.sqs.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=5,
                    VisibilityTimeout=VISIBILITY_TIMEOUT,
                    AttributeNames=['All'],
                    MessageAttributeNames=['All'] 
                )

                messages = response.get("Messages", [])

                if not messages:
                    await asyncio.sleep(1)
                    continue

                for message in messages:
                    body = json.loads(message["Body"])
                    receipt = message["ReceiptHandle"]
                    retry_count = int(message.get("Attributes", {}).get("ApproximateReceiveCount", "1"))

                    print(f"Received message: {body} (Attempt {retry_count})")
                    
                    if retry_count >= MAX_RECEIVE_COUNT:
                        print(f"Max retries reached for {body['report_id']}. Marking as failed.")
                        async with AsyncSessionLocal() as session:
                            success = await self.mark_failed(session, body["report_id"])
                            if success:
                                self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt)
                                print(f"Marked {body['report_id']} as failed and deleted message")
                        continue

                    success = await self.process_report(body["report_id"], receipt)

                    if success:
                        print(f"Successfully processed and deleted message: {body}\n")
                    else:
                        print(f"Worker failed for {body}. Will retry.\n")
        except KeyboardInterrupt:
            print("\nShutting down worker...")
            cleanup_task.cancel()
            raise
        except Exception as e:
            print(f"Unexpected error in worker main loop: {e}")
            cleanup_task.cancel()
            raise

    async def periodic_cleanup(self):
        #clean every 10 mins
        while True:
            try:
                await asyncio.sleep(600)
                async with AsyncSessionLocal() as session:
                    service = ReportsService(
                        session,
                        ReportRepository(),
                        None,
                        None,
                        S3ReportStorageAdapter(),
                        SQSReportQueueAdapter(),
                        EmailNotificationAdapter()
                    )
                    
                    count = await service.cleanup_stuck_reports(timeout_minutes=30)
                    if count > 0:
                        print(f"Periodic cleanup: marked {count} stuck reports as failed")
                        
            except asyncio.CancelledError:
                print("Periodic cleanup task cancelled")
                break
            except Exception as e:
                print(f"Error in periodic cleanup: {e}")

    async def mark_failed(self, session, report_id) -> bool:
        try:
            repo = ReportRepository()
            report = await repo.get_by_id(session, report_id)
            if report:
                report.status = ReportStatus.failed
                await session.commit()
                
                try:
                    from app.modules.users.models import User
                    user = await session.get(User, report.user_id)
                    if user:
                        notification_service = EmailNotificationAdapter()
                        await notification_service.notify_report_failed(
                            user=user,
                            report=report
                        )
                except Exception as email_error:
                    print(f"Failed to send failure notification for report {report_id}: {email_error}")
                
                return True
            return False
        except Exception as e:
            print(f"Error marking report {report_id} as failed: {e}")
            return False

    async def cleanup_stuck_reports_on_startup(self):
        try:
            async with AsyncSessionLocal() as session:
                service = ReportsService(
                    session,
                    ReportRepository(),
                    None,
                    None,
                    S3ReportStorageAdapter(),
                    SQSReportQueueAdapter(),
                    EmailNotificationAdapter()
                )
                
                # Clean up reports stuck for more than 30 minutes
                count = await service.cleanup_stuck_reports(timeout_minutes=30)
                if count > 0:
                    print(f"Cleaned up {count} stuck reports from previous worker runs")
        except Exception as e:
            print(f"Error during startup cleanup: {e}")

    async def process_report(self, report_id: str, receipt_handle: str) -> bool:
        """Process a report and only delete SQS message if successful."""
        
        repo = ReportRepository()

        try:
            async with AsyncSessionLocal() as session:
                report = await repo.get_by_id(session, report_id)

                if not report:
                    print(f"Report {report_id} not found. Skipping.")
                    #delete message since report doesn't exist
                    self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)
                    return True

                if report.status == ReportStatus.completed:
                    print(f"{report_id} already completed - skipping.")
                    #delete message since work is already done
                    self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)
                    return True

                service = ReportsService(
                    session, 
                    repo, 
                    None, 
                    None, 
                    S3ReportStorageAdapter(), 
                    SQSReportQueueAdapter(), 
                    EmailNotificationAdapter()
                )

                #mark as processing with timestamp
                await service.mark_processing_started(report_id)

                print(f"Generating report for {report_id}...")
                await service.generate_now(report_id)
                print(f"Report done: {report.file_name}")
                
                self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)
                return True

        except Exception as e:
            try:
                async with AsyncSessionLocal() as session:
                    success = await self.mark_failed(session, report_id)
                    if success:
                        self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)
                        print(f"Marked {report_id} as failed and deleted message")
                        return True
            except Exception as commit_error:
                print(f"Error marking report {report_id} as failed: {commit_error}")
                
            print(f"Error generating {report_id}: {e}")
            return False


async def main():
    worker = ReportWorker()
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
