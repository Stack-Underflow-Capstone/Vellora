from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import boto3
from botocore.config import Config

from app.config import settings
from app.modules.expenses.exceptions import ReceiptStorageConfigError


@dataclass
class ReceiptStorage:
    bucket: str
    region: str
    _client: any
    presign_seconds: int = 900  # 15 minutes

    @classmethod
    def from_settings(cls) -> "ReceiptStorage":
        if not settings.AWS_S3_BUCKET or not settings.AWS_REGION:
            raise ReceiptStorageConfigError("AWS_S3_BUCKET and AWS_REGION must be set to store receipts")

        client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            config=Config(s3={"addressing_style": "path"}),
        )
        return cls(
            bucket=settings.AWS_S3_BUCKET,
            region=settings.AWS_REGION,
            _client=client,
            presign_seconds=settings.RECEIPT_URL_EXPIRES_SECONDS,
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.bucket)

    def upload_bytes(self, *, key: str, content: bytes, content_type: str) -> None:
        self._client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content,
            ContentType=content_type,
            ServerSideEncryption="AES256",
        )

    def generate_presigned_url(self, key: str, expires_in: Optional[int] = None) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in or self.presign_seconds,
        )
