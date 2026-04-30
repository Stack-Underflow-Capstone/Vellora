import uuid

import botocore
from app.aws_client import get_s3_client
from app.config import settings
from app.modules.reports.ports import StoragePort


class S3ReportStorageAdapter(StoragePort):
    
    def __init__(self):
        self.s3 = get_s3_client()
        self.bucket = settings.REPORTS_BUCKET

    def save(self, report_id: uuid.UUID, file_bytes: bytes) -> str:
        file_name = f"report_{report_id}.pdf"
        
        self.s3.put_object(
            Bucket=self.bucket,
            Key=file_name,
            Body=file_bytes,
            ContentType="application/pdf"
        )

        return file_name

    def get_signed_url(self, key: str, expires_in: int = 300) -> str:
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in
        )
    
    def exists(self, key: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def delete(self, key: str) -> bool:
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
            return True
        except botocore.exceptions.ClientError:
            return False