import pytest
from sqlalchemy import inspect


@pytest.mark.asyncio
async def test_core_tables_exist(async_engine, reset_database):
    async with async_engine.begin() as conn:
        tables = await conn.run_sync(lambda sync_conn: set(inspect(sync_conn).get_table_names()))
    assert {"users", "refresh_tokens", "oauth_accounts", "oauth_states"} <= tables
