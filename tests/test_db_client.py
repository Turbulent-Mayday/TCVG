import os
from unittest.mock import patch

import pytest

from src.database.db_client import LocalSQLiteClient, get_db_client


@pytest.mark.asyncio
async def test_local_sqlite_lifecycle(tmp_path):
    """Verifies the complete asynchronous lifecycle of LocalSQLiteClient.

    Ensures connection instantiation, DDL execution, atomic batch transactions,
    row-factory dictionary mapping, and strict post-exit teardown locks.
    """
    db_file = tmp_path / "lifecycle.db"
    client = LocalSQLiteClient(f"://{db_file}")
    assert client.db_path == db_file, (
        f"Path resolution mismatch: expected {db_file}, got {client.db_path}"
    )

    async with client as active_client:
        assert active_client.conn is not None, (
            "SQLite connection handle failed to initialize on context entry"
        )
        await active_client.execute(
            "CREATE TABLE test_cards (id INTEGER PRIMARY KEY, name TEXT);"
        )
        await active_client.batch(
            [
                "INSERT INTO test_cards (id, name) VALUES (1, 'Orc Warrior');",
                "INSERT INTO test_cards (id, name) VALUES (2, 'Dwarf Shaman');",
            ]
        )
        rows = await active_client.execute("SELECT * FROM test_cards ORDER BY id;")
        assert len(rows) == 2, f"Expected 2 persisted records, fetched {len(rows)}"
        assert rows[0]["name"] == "Orc Warrior"
        assert rows[1]["name"] == "Dwarf Shaman"

    with pytest.raises(
        RuntimeError, match="Database connection has not been initialized."
    ):
        await client.execute("SELECT * FROM test_cards;")


@pytest.mark.asyncio
async def test_local_sqlite_uninitialized_batch(tmp_path):
    """Ensures batch execution rejects operations on uninitialized connection handles."""
    client = LocalSQLiteClient(f"://{tmp_path / 'uninit.db'}")
    with pytest.raises(
        RuntimeError, match="Database connection has not been initialized."
    ):
        await client.batch(["SELECT 1;"])


def test_get_db_client_routing_local():
    """Confirms colon-prefixed URLs route directly to the zero-dependency LocalSQLiteClient."""
    with patch.dict(os.environ, {"DATABASE_URL": "://test.db"}):
        client = get_db_client()
        assert isinstance(client, LocalSQLiteClient), (
            "Dispatcher failed to instantiate LocalSQLiteClient for local URI"
        )
        assert client.db_path.name == "test.db"


def test_get_db_client_routing_remote():
    """Confirms remote libsql/https URIs delegate connection initialization to libsql_client."""
    with (
        patch.dict(
            os.environ,
            {
                "DATABASE_URL": "libsql://i.love.berserk",
                "DATABASE_AUTH_TOKEN": "BERSERK",
            },
        ),
        patch("libsql_client.create_client") as mock_create_client,
    ):
        get_db_client()
        mock_create_client.assert_called_once_with(
            url="libsql://i.love.berserk", auth_token="BERSERK"
        )


def test_get_db_client_missing_env():
    """Validates that an unset DATABASE_URL triggers an immediate configuration ValueError."""
    with (
        patch.dict(os.environ, {}, clear=True),
        pytest.raises(ValueError, match="Critical configuration missing"),
    ):
        get_db_client()
