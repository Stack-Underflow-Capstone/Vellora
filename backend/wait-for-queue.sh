#!/bin/bash
set -e

QUEUE_NAME=${REPORTS_QUEUE:-generateReports-queue}
MAX_RETRIES=30
RETRY_DELAY=2

echo "Waiting for SQS queue '${QUEUE_NAME}' to be available..."

for i in $(seq 1 $MAX_RETRIES); do
  if python3 -c "
from app.config import settings
from app.aws_client import get_sqs_client
from botocore.exceptions import ClientError
try:
    sqs = get_sqs_client()
    result = sqs.get_queue_url(QueueName='${QUEUE_NAME}')
    print('SUCCESS')
    exit(0)
except ClientError as e:
    if e.response.get('Error', {}).get('Code') == 'AWS.SimpleQueueService.NonExistentQueue':
        exit(1)
    raise
" 2>/dev/null; then
    echo "Queue ${QUEUE_NAME} is available!"
    break
  fi
  
  if [ $i -eq $MAX_RETRIES ]; then
    echo "ERROR: Queue ${QUEUE_NAME} not found after ${MAX_RETRIES} attempts"
    exit 1
  fi
  
  echo "Queue not found. Waiting ${RETRY_DELAY} seconds... (Attempt ${i}/${MAX_RETRIES})"
  sleep $RETRY_DELAY
done

echo "Starting worker..."
exec python -m app.worker

