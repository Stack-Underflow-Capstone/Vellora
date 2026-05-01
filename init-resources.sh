#!/bin/bash
set -e

# Create S3 bucket
echo "[INFO] Creating S3 bucket..."
awslocal s3 mb s3://vellora-s3-bucket
awslocal s3 mb s3://vellora-receipts-dev

echo "[INFO] Setting up CORS configuration for S3 bucket..."
awslocal s3api put-bucket-cors --bucket vellora-s3-bucket --cors-configuration '{
    "CORSRules": [
        {
            "AllowedOrigins": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST"],
            "AllowedHeaders": ["*"],
            "MaxAgeSeconds": 3000
        }
    ]
}'
awslocal s3api put-bucket-cors --bucket vellora-receipts-dev --cors-configuration '{
    "CORSRules": [
        {
            "AllowedOrigins": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST"],
            "AllowedHeaders": ["*"],
            "MaxAgeSeconds": 3000
        }
    ]
}'

# Create SQS queues
echo "[INFO] Creating SQS queues..."
awslocal sqs create-queue --queue-name sendNotif-queue
awslocal sqs create-queue --queue-name generateReports-queue

# (Optional) Create RDS (LocalStack emulates the RDS control plane, not data)
echo "[INFO] Creating RDS instance..."
awslocal rds create-db-instance \
    --db-instance-identifier db1 \
    --engine postgres \
    --db-instance-class db.t2.micro \
    --allocated-storage 20 \
    --master-username myuser \
    --master-user-password mypassword \
    --backup-retention-period 3

# Create CloudFront distribution (for static assets)
echo "[INFO] Creating CloudFront distribution..."
awslocal cloudfront create-distribution --origin-domain-name vellora-files.s3.localstack.cloud

echo "[INFO] Verifying SES email address..."
awslocal ses verify-email-identity --email hello@example.com