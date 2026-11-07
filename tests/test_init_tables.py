import os
from unittest.mock import patch

import pytest

from src.database.db_client import get_db_client
from src.sql.init_tables import get_supported_games, init_all_tables


def test_get_supported_games():
    """Verifies whitespace trimming, case normalization, and empty-token filtering for game codes."""
    with patch.dict(
        os.environ, {"SUPPORTED_GAMES": "berserk, MTG, ONE PIECE Card Game  , "}
    ):
        games = get_supported_games()
        assert games == ["berserk", "mtg", "one piece card game"]


def test_get_supported_games_missing():
    """Ensures missing SUPPORTED_GAMES configuration aborts startup with ValueError."""
    with (
        patch.dict(os.environ, {}, clear=True),
        pytest.raises(ValueError, match="Critical configuration missing"),
    ):
        get_supported_games()


@pytest.mark.asyncio
async def test_init_all_tables_empty_list(capsys):
    """Confirms bootstrapper exits gracefully with a telemetry warning when no valid games are parsed."""
    with patch.dict(os.environ, {"SUPPORTED_GAMES": " , , "}):
        await init_all_tables()
        captured = capsys.readouterr()
        assert "SUPPORTED_GAMES is empty" in captured.out


@pytest.mark.asyncio
async def test_init_all_tables_creation():
    """Executes an end-to-end schema and B-Tree index bootstrap against an ephemeral SQLite catalog."""
    await init_all_tables()

    async with get_db_client() as client:
        table_rows = await client.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        )
        tables = [r["name"] for r in table_rows]
        assert "cards_berserk" in tables, (
            "Target relation 'cards_berserk' was not materialized in sqlite_master"
        )

        index_rows = await client.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';"
        )
        indices = [r["name"] for r in index_rows]
        assert "idx_berserk_name_norm" in indices
        assert "idx_berserk_set_num" in indices
        assert "idx_berserk_indirect" in indices
