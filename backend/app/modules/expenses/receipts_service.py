import logging
import secrets
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.modules.expenses.exceptions import (
    ReceiptStorageConfigError,
    ReceiptUploadError,
    ReceiptValidationError,
)
from app.modules.expenses.models import ExpenseReceipt
from app.modules.expenses.receipts_repository import ExpenseReceiptRepo
from app.modules.expenses.schemas import ExpenseReceiptDTO
from app.modules.trips.exceptions import TripNotFoundError
from app.modules.trips.repository import TripRepo
from app.core.storage import ReceiptStorage


logger = logging.getLogger(__name__)


MAX_RECEIPT_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES: set[str] = {
    "image/jpeg",
    "image/png",
    "application/pdf",
}


class ExpenseReceiptsService:
    def __init__(
        self,
        trip_repo: TripRepo,
        receipt_repo: ExpenseReceiptRepo,
        storage: ReceiptStorage,
    ):
        self.trip_repo = trip_repo
        self.receipt_repo = receipt_repo
        self.storage = storage

    async def _ensure_trip(self, user_id: UUID, trip_id: UUID):
        trip = await self.trip_repo.get(trip_id, user_id)
        if not trip:
            raise TripNotFoundError("Trip not found or not owned by user")
        return trip

    def _validate_file(self, upload: UploadFile, content: bytes) -> None:
        if not upload.filename:
            raise ReceiptValidationError("File name is required")
        if upload.content_type not in ALLOWED_CONTENT_TYPES:
            raise ReceiptValidationError("Only JPEG, PNG, or PDF receipts are allowed")
        if len(content) == 0:
            raise ReceiptValidationError("Empty files are not allowed")
        if len(content) > MAX_RECEIPT_BYTES:
            raise ReceiptValidationError("File is too large (max 10 MB)")

    def _build_object_key(self, trip_id: UUID, filename: str) -> str:
        safe_name = Path(filename).name.replace(" ", "_")
        unique_prefix = secrets.token_hex(8)
        return f"trips/{trip_id}/receipts/{unique_prefix}_{safe_name}"

    async def upload_receipt(
        self,
        user_id: UUID,
        trip_id: UUID,
        expense_id: UUID | None,
        upload: UploadFile,
    ) -> ExpenseReceiptDTO:
        await self._ensure_trip(user_id, trip_id)

        try:
            content = await upload.read()
        except Exception as exc:  # pragma: no cover - unexpected IO error
            raise ReceiptUploadError("Failed to read uploaded file") from exc

        self._validate_file(upload, content)

        if not self.storage.is_configured:
            raise ReceiptStorageConfigError("Receipt storage is not configured")

        object_key = self._build_object_key(trip_id, upload.filename or "receipt")

        try:
            self.storage.upload_bytes(
                key=object_key,
                content=content,
                content_type=upload.content_type or "application/octet-stream",
            )
        except Exception as exc:  # pragma: no cover - network/storage errors
            logger.exception("Receipt storage upload failed for %s", object_key)
            raise ReceiptUploadError("Failed to upload receipt to storage") from exc

        receipt = ExpenseReceipt(
            id=uuid.uuid4(),
            expense_id=None,
            trip_id=trip_id,
            user_id=user_id,
            bucket=self.storage.bucket,
            object_key=object_key,
            file_name=upload.filename or "receipt",
            content_type=upload.content_type or "application/octet-stream",
            size_bytes=len(content),
        )

        try:
            saved = await self.receipt_repo.create(receipt)
        except Exception as exc:  # pragma: no cover - db errors
            raise ReceiptUploadError("Failed to persist receipt metadata") from exc

        download_url = self.storage.generate_presigned_url(object_key)
        return ExpenseReceiptDTO.model_validate(
            {
                "id": saved.id,
                "file_name": saved.file_name,
                "content_type": saved.content_type,
                "size_bytes": saved.size_bytes,
                "created_at": saved.created_at,
                "download_url": download_url,
            }
        )

    async def list_receipts(
        self,
        user_id: UUID,
        trip_id: UUID,
        expense_id: UUID | None,
    ) -> list[ExpenseReceiptDTO]:
        await self._ensure_trip(user_id, trip_id)
        receipts = await self.receipt_repo.list_for_trip(trip_id, user_id)
        if not receipts:
            return []

        def to_dto(rcpt: ExpenseReceipt):
            return ExpenseReceiptDTO.model_validate(
                {
                    "id": rcpt.id,
                    "file_name": rcpt.file_name,
                    "content_type": rcpt.content_type,
                    "size_bytes": rcpt.size_bytes,
                    "created_at": rcpt.created_at,
                    "download_url": self.storage.generate_presigned_url(rcpt.object_key),
                }
            )

        return [to_dto(r) for r in receipts]
