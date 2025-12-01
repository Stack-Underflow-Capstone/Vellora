#!/bin/bash

echo "$(date '+%Y-%m-%d %H:%M:%S') [ENTRYPOINT] Starting wait-for-postgres script..."

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h postgres -p 5432 -U postgres; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "PostgreSQL is ready!"
echo "Running database migrations..."
alembic upgrade head
echo "Migrations complete"

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload