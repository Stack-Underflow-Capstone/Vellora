import os, importlib, asyncio
from logging.config import fileConfig
from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from app.core.base import Base

from dotenv import load_dotenv
load_dotenv()

from app.modules.users import models
from app.modules.auth import models
from app.modules.trips import models
from app.modules.expenses import models
from app.modules.rate_customizations import models
from app.modules.rate_categories import models
from app.modules.common_places import models
from app.modules.reports import models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL is not set")
config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata,
        literal_binds=True, dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.", poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
