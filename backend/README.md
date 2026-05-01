
## Dev guide

If you want the latest copy of this guide on GitHub, read [the backend README](https://github.com/Stack-Underflow-Capstone/Vellora/tree/dev/backend#readme). If you only need the AI endpoint details, use [AI_TRIP_ASSISTANT.md](AI_TRIP_ASSISTANT.md).

### Before You Start

Install these first:

- [Git](https://git-scm.com/downloads)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) if you want the Docker setup
- [Python 3.11 or newer](https://www.python.org/downloads/) if you want the non-Docker setup
- [PostgreSQL](https://www.postgresql.org/download/) for local development without Docker
- [LocalStack](https://docs.localstack.cloud/getting-started/installation/) if you want to run S3/SQS locally without Docker

Optional accounts and dashboards:

- [Google Cloud Console](https://console.cloud.google.com/) for Google OAuth credentials
- [Resend](https://resend.com/) for email sending
- [OpenAI platform](https://platform.openai.com/) for a real AI API key

### Setup with Docker

Use this if you want the simplest path for the backend. Docker starts Postgres, LocalStack, the backend, and the worker.

#### 1. Clone the repo

```bash
git clone https://github.com/Stack-Underflow-Capstone/Vellora.git
cd Vellora
```

#### 2. Open the project in VS Code

```bash
code .
```

If `code .` does not work, open VS Code manually and use File > Open Folder.

#### 3. Set up the environment file for Docker

1. Go into the backend folder and create the `.env` file there:

```bash
cd backend
```

2. Add the environment variables the app needs. Use your own values for the secret ones, and keep the non-secret values below as a starting point:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/Vellora

# Security
JWT_SECRET_KEY=replace_with_a_long_random_secret
FERNET_KEY=replace_with_a_valid_fernet_key

# Google OAuth
OAUTH_PROVIDERS__GOOGLE__CLIENT_ID=your_google_client_id
OAUTH_PROVIDERS__GOOGLE__CLIENT_SECRET=your_google_client_secret
OAUTH_PROVIDERS__GOOGLE__REDIRECT_URI=http://127.0.0.1:8000/api/v1/auth/providers/google/callback
OAUTH_PROVIDERS__GOOGLE__SCOPES=["openid","email","profile"]
OAUTH_STATE_TTL_SECONDS=1800

# LocalStack
USE_LOCALSTACK=true
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=us-east-1
LOCALSTACK_ENDPOINT=http://localstack:4566
REPORTS_BUCKET=vellora-s3-bucket
REPORTS_QUEUE=generateReports-queue
AWS_S3_BUCKET=vellora-s3-bucket
AWS_S3_ENDPOINT_URL=http://localstack:4566

# LocalStack Pro
LOCALSTACK_AUTH_TOKEN=your_localstack_pro_token

# Email
EMAIL_SENDER=noreply@resend.dev
EMAIL_ENABLED=true
EMAIL_PROVIDER=resend
RESEND_API_KEY=your_resend_api_key

# App URL
BACKEND_URL=http://localhost:8000

# AI / weather
AI_AGENT_ENABLED=false
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
AI_TIMEOUT_SECONDS=30
AI_RATE_LIMIT_PER_MINUTE=12
AI_MAX_METADATA_KEYS=20
AI_MAX_METADATA_VALUE_LENGTH=500
AI_MAX_MISSING_DETAILS=8
WEATHER_BASE_URL=https://api.open-meteo.com/v1/forecast
WEATHER_TIMEOUT_SECONDS=10
```

3. Fill in the secret values from the services you use:

- `JWT_SECRET_KEY` and `FERNET_KEY` should be generated locally.
- `OAUTH_PROVIDERS__GOOGLE__CLIENT_ID` and `OAUTH_PROVIDERS__GOOGLE__CLIENT_SECRET` come from [Google Cloud Console](https://console.cloud.google.com/).
- `RESEND_API_KEY` comes from [Resend](https://resend.com/) if you want email to work.
- `OPENAI_API_KEY` comes from [OpenAI platform](https://platform.openai.com/) if you want real AI responses.
- `LOCALSTACK_AUTH_TOKEN` is only needed if you are using the LocalStack Pro image from Docker.

To generate the two local security values, run these commands in a terminal from the backend folder:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Use the first command output for `JWT_SECRET_KEY` and the second command output for `FERNET_KEY`.

#### 4. Make sure the shell scripts uses the correct line endings based on OS

Windows Users: Before running Docker commands, make sure all `.sh` script files have LF line endings instead of CRLF:

1. Open `init-resources.sh` and `wait-for-postgres.sh` in VS Code
2. Click on `CRLF` in the bottom status bar and change to `LF`
3. Save the files (don't commit these changes)

Mac Users: No changes Required

#### 5. Start everything

Stay in the backend folder and run Docker Compose from there:

```bash
docker compose -f ../docker-compose.yml --env-file .env up -d --build
```

This starts the services defined in the repo root compose file. The frontend container may also start because it is part of that file, but you can ignore it if you only care about backend work.

If you only change values in `backend/.env`, run the same command again without `--build` so Docker picks up the new variables without rebuilding everything:

```bash
docker compose -f ../docker-compose.yml --env-file .env up -d
```

#### 6. Wait for startup

Give it a minute or two. On first run, Docker has to pull images, create containers, run migrations, and start the worker.

#### 7. Open the backend docs

```text
http://localhost:8000/docs
```

If that page does not open, check `docker compose logs backend` and make sure the env file values were loaded from the correct place.

#### 8. Check LocalStack if you need it

LocalStack should already be running in Docker. You can verify it with:

```bash
docker exec -it localstack awslocal sqs list-queues
docker exec -it localstack awslocal s3 ls
```

The `init-resources.sh` script creates the buckets and queues the app expects.

Important: the worker starts automatically in Docker. You do not need to run `python -m app.worker` separately.

If you use the reports download endpoint in Docker, the URL may start with `http://localstack:4566/`. That will not open in your browser. Replace `localstack` with `localhost` so the URL looks like `http://localhost:4566/...`.

### Important Email Testing Note

As long as we don't have a verified domain and use the testing/dev email `noreply@resend.dev`, you won't be able to send emails to anyone other than your own account. If you want to test email functionality, you will need to:

1. Create your own [Resend account](https://resend.com/)
2. Generate an API key
3. Update `RESEND_API_KEY` in your `.env` file

Only emails sent to your verified Resend account email will be delivered.

### Setup without Docker

Use this if you want to run the backend directly on your machine.

#### 1. Install the tools

- [Git](https://git-scm.com/downloads)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Python 3.11 or newer](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [LocalStack](https://docs.localstack.cloud/getting-started/installation/) if you need report/S3/SQS features locally

#### 2. Clone the repo

```bash
git clone https://github.com/Stack-Underflow-Capstone/Vellora.git
cd Vellora/backend
```

#### 3. Open the backend in VS Code

```bash
code .
```

If `code .` does not work, open VS Code manually and use File > Open Folder.

#### 4. Prepare PostgreSQL

Ensure your PostgreSQL server is running and that you have created a database for the app.

Set your database connection by creating the `DATABASE_URL` environment variable in `backend/.env`.

Example:

```text
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/Vellora
```

#### 5. Create the backend `.env` file

Put a `.env` file in the `backend` folder for non-Docker runs. Use this layout as a starting point:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/Vellora

# Security
JWT_SECRET_KEY=replace_with_a_long_random_secret
FERNET_KEY=replace_with_a_valid_fernet_key

# Google OAuth
OAUTH_PROVIDERS__GOOGLE__CLIENT_ID=your_google_client_id
OAUTH_PROVIDERS__GOOGLE__CLIENT_SECRET=your_google_client_secret
OAUTH_PROVIDERS__GOOGLE__REDIRECT_URI=http://127.0.0.1:8000/api/v1/auth/providers/google/callback
OAUTH_PROVIDERS__GOOGLE__SCOPES=["openid","email","profile"]
OAUTH_STATE_TTL_SECONDS=1800

# LocalStack
USE_LOCALSTACK=true
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=us-east-1
LOCALSTACK_ENDPOINT=http://localhost:4566
REPORTS_BUCKET=vellora-s3-bucket
REPORTS_QUEUE=generateReports-queue
AWS_S3_BUCKET=vellora-s3-bucket
AWS_S3_ENDPOINT_URL=http://localhost:4566

# LocalStack Pro
LOCALSTACK_AUTH_TOKEN=your_localstack_pro_token

# Email
EMAIL_SENDER=noreply@resend.dev
EMAIL_ENABLED=true
EMAIL_PROVIDER=resend
RESEND_API_KEY=your_resend_api_key

# App URL
BACKEND_URL=http://localhost:8000

# AI / weather
AI_AGENT_ENABLED=false
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
AI_TIMEOUT_SECONDS=30
AI_RATE_LIMIT_PER_MINUTE=12
AI_MAX_METADATA_KEYS=20
AI_MAX_METADATA_VALUE_LENGTH=500
AI_MAX_MISSING_DETAILS=8
WEATHER_BASE_URL=https://api.open-meteo.com/v1/forecast
WEATHER_TIMEOUT_SECONDS=10
```

For non-Docker runs, keep these values:

- `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/Vellora`
- `LOCALSTACK_ENDPOINT=http://localhost:4566`
- `AWS_S3_ENDPOINT_URL=http://localhost:4566`

For Docker runs, keep these values:

- `DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/Vellora`
- `LOCALSTACK_ENDPOINT=http://localstack:4566`
- `AWS_S3_ENDPOINT_URL=http://localstack:4566`

#### 6. Fill in the secret values

- `JWT_SECRET_KEY` and `FERNET_KEY` should be generated locally.
- `OAUTH_PROVIDERS__GOOGLE__CLIENT_ID` and `OAUTH_PROVIDERS__GOOGLE__CLIENT_SECRET` come from [Google Cloud Console](https://console.cloud.google.com/).
- `RESEND_API_KEY` comes from [Resend](https://resend.com/) if you want email to work.
- `OPENAI_API_KEY` comes from [OpenAI platform](https://platform.openai.com/) if you want real AI responses.
- `LOCALSTACK_AUTH_TOKEN` is only needed if you are using the LocalStack Pro image from Docker.

To generate the two local security values, run these commands in a terminal from the backend folder:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Use the first command output for `JWT_SECRET_KEY` and the second command output for `FERNET_KEY`.

#### 7. Set up LocalStack if you need it

If you want the report and storage features, start LocalStack locally and create the buckets and queues the app uses.

1. Install the [LocalStack CLI](https://docs.localstack.cloud/getting-started/installation/).
2. Create a folder like `C:\dev\localstack`.
3. Create a `docker-compose.yml` file in that folder with this content:

```yaml
services:
  localstack:
    container_name: localstack
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,sqs
      - DEBUG=1
      - AWS_DEFAULT_REGION=us-east-1
    volumes:
      - "./data:/var/lib/localstack"
```

4. Start LocalStack from that folder:

```bash
docker compose up -d
```

5. Configure AWS CLI with the localstack profile:

```bash
aws configure --profile localstack
```

When it asks for values, use these:

```text
AWS Access Key ID [None]: test
AWS Secret Access Key [None]: test
Default region name [None]: us-east-1
Default output format [None]: json
```

6. Create the buckets and queues the app expects:

```bash
aws --endpoint-url=http://localhost:4566 s3api create-bucket --bucket vellora-s3-bucket --profile localstack
aws --endpoint-url=http://localhost:4566 s3api create-bucket --bucket vellora-receipts-dev --profile localstack
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name sendNotif-queue --profile localstack
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name generateReports-queue --profile localstack
```

If you already have the rest of the app running without Docker, point `LOCALSTACK_ENDPOINT` at `http://localhost:4566`.

If you use the reports download endpoint while running LocalStack locally, use the localhost version of the URL in your browser.

### Important Email Testing Note

As long as we don't have a verified domain and use the testing/dev email `noreply@resend.dev`, you won't be able to send emails to anyone other than your own account. If you want to test email functionality, you will need to:

1. Create your own [Resend account](https://resend.com/)
2. Generate an API key
3. Update `RESEND_API_KEY` in your `.env` file

Only emails sent to your verified Resend account email will be delivered.

If you do not need report generation, S3, or SQS while running locally, you can still keep the LocalStack section in place but skip starting the LocalStack container until you need those features.

Before creating the virtual environment, make sure your terminal is in the backend folder:

```bash
cd backend
```

#### 8. Create a virtual environment on Windows

```bash
python -m venv .venv
```

#### 9. Activate the virtual environment

```bash
.venv\Scripts\activate
```

#### 10. Install dependencies

```bash
pip install -r requirements.txt
```

#### 11. Run database migrations

```bash
alembic upgrade head
```

#### 12. Start the API server

```bash
fastapi dev app/main.py
```

Open:

```text
http://localhost:8000/docs
```

#### 13. Start the worker in a second terminal

Use this if you want background jobs like notifications and report generation.

```bash
cd backend
.venv\Scripts\activate
python -m app.worker
```

Quick endpoint reference:

- Docker: `DATABASE_URL=...@postgres:5432/...`, `LOCALSTACK_ENDPOINT=http://localstack:4566`, `AWS_S3_ENDPOINT_URL=http://localstack:4566`
- Non-Docker: `DATABASE_URL=...@localhost:5432/...`, `LOCALSTACK_ENDPOINT=http://localhost:4566`, `AWS_S3_ENDPOINT_URL=http://localhost:4566`

### Creating a new feature

#### 1. Create folder in module folder

ex:
```
app/modules/trips/
```

#### 2. Inside it, create these files and write your code:

```
router.py        # FastAPI endpoints
service.py       # Business logic
repository.py    # DB queries (using async SQLAlchemy)
models.py        # ORM models (inherit from Base)
schemas.py       # Pydantic request/response models
__init__.py
```

#### 2. Inside it, create these files and write your code:

Alembic only sees your models if they’re imported inside:
```
app/infra/migrations/env.py
```

So add this line at the top:
```python
from app.modules.trips import models  #"app.modules.<name of folder>"
```

That’s all don’t modify anything else in `env.py`.

#### 3. Generating and Applying Migrations

Whenever you add or change a model:

First Generate a migration file
```
alembic revision --autogenerate -m "desc of what u did in model"
```
Then Apply the migration
```
alembic upgrade head
```
You can undo migrations if u ever need to.

#### 4. Registering your router

After creating your router, you must include it in the global API.

Open:
```
app/api/v1/router.py
```
Add:
```python
from app.modules.trips.router import router as trips_router #app.modules.<folder name>.router
router.include_router(trips_router)
```

