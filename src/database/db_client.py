import os
import sqlite3
from pathlib import Path
from typing import Any

import libsql_client
from dotenv import load_dotenv

load_dotenv()


class LocalSQLiteClient:
    """Zero-dependency asynchronous client for local SQLite databases.

    Supports uniform interfaces across execute, batch, and context manager
    workflows without external network dependencies.
    """

    def __init__(self, file_url: str) -> None:
        raw_path = file_url.removeprefix(":")
        self.db_path = Path(raw_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: sqlite3.Connection | None = None

    async def __aenter__(self) -> "LocalSQLiteClient":
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.conn:
            self.conn.close()

    async def execute(self, sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        if not self.conn:
            raise RuntimeError("Database connection has not been initialized.")
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur.fetchall()

    async def batch(self, statements: list[str]) -> None:
        if not self.conn:
            raise RuntimeError("Database connection has not been initialized.")
        cur = self.conn.cursor()
        for stmt in statements:
            cur.execute(stmt)
        self.conn.commit()


def get_db_client() -> Any:
    """Connection factory dispatching between local SQLite and remote libSQL.

    Routes paths starting with ':' to LocalSQLiteClient,
    and remote protocols (libsql://, https://) to libsql_client.
    """
    url = os.getenv("DATABASE_URL")
    token = os.getenv("DATABASE_AUTH_TOKEN")

    if not url:
        raise ValueError("Critical configuration missing: DATABASE_URL environment variable is not set.")

    if url.startswith(":"):
        return LocalSQLiteClient(url)

    return libsql_client.create_client(url=url, auth_token=token)