import asyncio
import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database import get_db_client
from src.sql import load_game_sql, load_game_sql_statements

load_dotenv()


def get_supported_games() -> list[str]:
    """Parses comma-separated game codes from the SUPPORTED_GAMES environment variable."""
    raw_games = os.getenv("SUPPORTED_GAMES")
    if not raw_games:
        raise ValueError("Critical configuration missing: SUPPORTED_GAMES environment variable is not set.")
    return [game.strip().lower() for game in raw_games.split(",") if game.strip()]


async def init_all_tables() -> None:
    """Applies generated DDL schemas and composite indices for configured games."""
    games = get_supported_games()
    if not games:
        print("[Schema Bootstrapper] Warning: SUPPORTED_GAMES is empty. No tables initialized.")
        return

    async with get_db_client() as client:
        for game in games:
            schema_sql = load_game_sql(game=game, query_type="schema")
            await client.execute(schema_sql)

            index_statements = load_game_sql_statements(game=game, query_type="indices")
            if index_statements:
                await client.batch(index_statements)
            print(f"[Schema Bootstrapper] DDL schema and B-Tree indices applied for 'cards_{game}'.")


if __name__ == "__main__":
    asyncio.run(init_all_tables())