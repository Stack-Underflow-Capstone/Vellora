import boto3
from app.config import settings


def get_sqs_client():
    return boto3.client(
        "sqs",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
        endpoint_url=settings.LOCALSTACK_ENDPOINT if settings.USE_LOCALSTACK else None
    )

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
        endpoint_url=settings.LOCALSTACK_ENDPOINT if settings.USE_LOCALSTACK else None
    )