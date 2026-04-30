import io
import uuid
from datetime import datetime, timezone

import pytest
from fastapi import UploadFile

from app.modules.expenses.exceptions import (
    ReceiptStorageConfigError,
    ReceiptUploadError,
    ReceiptValidationError,
)
from app.modules.expenses.models import ExpenseReceipt
from app.modules.expenses.receipts_service import ExpenseReceiptsService
from app.modules.trips.exceptions import TripNotFoundError


class DummyStorage:
    def __init__(self, bucket: str = "test-bucket"):
        self.bucket = bucket
        self.uploaded = []
        self._presigned = "https://example.com/download"
        self.is_configured = bool(bucket)

    def upload_bytes(self, *, key: str, content: bytes, content_type: str) -> None:
        self.uploaded.append((key, content, content_type))

    def generate_presigned_url(self, key: str, expires_in: int | None = None) -> str:
        return f"{self._presigned}/{key}"


def make_upload(filename: str, content_type: str, data: bytes) -> UploadFile:
    upload = UploadFile(filename=filename, file=io.BytesIO(data))
    
    upload.headers = {"content-type": content_type}
    return upload


@pytest.mark.asyncio
async def test_upload_receipt_happy_path(monkeypatch):
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    expense_id = uuid.uuid4()

    async def _get_trip(self, tid, uid):
        return object()

    trip_repo = type("TRepo", (), {"get": _get_trip})()

    created_receipt = ExpenseReceipt(
        id=uuid.uuid4(),
        expense_id=None,
        trip_id=trip_id,
        user_id=user_id,
        bucket="test-bucket",
        object_key="key",
        file_name="receipt.png",
        content_type="image/png",
        size_bytes=4,
        created_at=datetime.now(timezone.utc),
    )

    async def _create(self, r):
        if getattr(r, "created_at", None) is None:
            r.created_at = datetime.now(timezone.utc)
        return r

    async def _list_for_expense(self, eid, uid=None):
        return [created_receipt]

    receipts_repo = type(
        "RRepo",
        (),
        {
            "create": _create,
            "list_for_trip": _list_for_expense,
        },
    )()

    storage = DummyStorage()
    svc = ExpenseReceiptsService(trip_repo, receipts_repo, storage)

    upload = make_upload("receipt.png", "image/png", b"data")

    dto = await svc.upload_receipt(user_id, trip_id, expense_id, upload)

    assert dto.file_name == "receipt.png"
    assert dto.content_type == "image/png"
    assert dto.size_bytes == 4
    assert dto.download_url.endswith("receipt.png")
    assert storage.uploaded  # upload called


@pytest.mark.asyncio
async def test_upload_receipt_rejects_invalid_type():
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    expense_id = uuid.uuid4()
    async def _get_trip(self, tid, uid):
        return object()

    trip_repo = type("TRepo", (), {"get": _get_trip})()
    async def _create(self, r):
        if getattr(r, "created_at", None) is None:
            r.created_at = datetime.now(timezone.utc)
        return r

    receipts_repo = type("RRepo", (), {"create": _create})()
    storage = DummyStorage()
    svc = ExpenseReceiptsService(trip_repo, receipts_repo, storage)

    bad_upload = make_upload("malware.exe", "application/octet-stream", b"boom")
    with pytest.raises(ReceiptValidationError):
        await svc.upload_receipt(user_id, trip_id, expense_id, bad_upload)


@pytest.mark.asyncio
async def test_upload_receipt_missing_trip():
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    expense_id = uuid.uuid4()

    async def _missing(self, trip_id, uid):
        return None

    trip_repo = type("TRepo", (), {"get": _missing})()

    async def _create(self, r):
        if getattr(r, "created_at", None) is None:
            r.created_at = datetime.now(timezone.utc)
        return r

    receipts_repo = type("RRepo", (), {"create": _create})()
    storage = DummyStorage()
    svc = ExpenseReceiptsService(trip_repo, receipts_repo, storage)

    upload = make_upload("receipt.png", "image/png", b"data")
    with pytest.raises(TripNotFoundError):
        await svc.upload_receipt(user_id, trip_id, expense_id, upload)


@pytest.mark.asyncio
async def test_upload_receipt_storage_not_configured():
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    expense_id = uuid.uuid4()
    async def _get_trip(self, tid, uid):
        return object()

    trip_repo = type("TRepo", (), {"get": _get_trip})()
    async def _create(self, r):
        return r

    receipts_repo = type("RRepo", (), {"create": _create})()
    storage = DummyStorage(bucket="")  # not configured
    svc = ExpenseReceiptsService(trip_repo, receipts_repo, storage)

    upload = make_upload("receipt.png", "image/png", b"data")
    with pytest.raises(ReceiptStorageConfigError):
        await svc.upload_receipt(user_id, trip_id, expense_id, upload)


@pytest.mark.asyncio
async def test_list_receipts_returns_presigned_urls():
    user_id = uuid.uuid4()
    trip_id = uuid.uuid4()
    expense_id = uuid.uuid4()
    async def _get_trip(self, tid, uid):
        return object()

    trip_repo = type("TRepo", (), {"get": _get_trip})()

    receipt = ExpenseReceipt(
        id=uuid.uuid4(),
        expense_id=None,
        trip_id=trip_id,
        user_id=user_id,
        bucket="test-bucket",
        object_key="key/receipt.png",
        file_name="receipt.png",
        content_type="image/png",
        size_bytes=10,
        created_at=datetime.now(timezone.utc),
    )
    async def _list_for_trip(self, tid, uid=None):
        return [receipt]

    receipts_repo = type("RRepo", (), {"list_for_trip": _list_for_trip})()
    storage = DummyStorage()
    svc = ExpenseReceiptsService(trip_repo, receipts_repo, storage)

    dtos = await svc.list_receipts(user_id, trip_id, expense_id)
    assert len(dtos) == 1
    assert dtos[0].download_url.endswith("key/receipt.png")
