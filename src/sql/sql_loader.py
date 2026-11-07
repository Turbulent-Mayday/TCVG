import os
import re

SQL_DIR = os.path.dirname(os.path.abspath(__file__))


def validate_identifier(value: str) -> str:
    """Sanitizes identifiers to mitigate SQL injection and path traversal risks."""
    clean = value.lower().strip()
    if not re.match(r"^[a-z0-9_]+$", clean):
        raise ValueError(f"Invalid alphanumeric identifier: '{value}'")
    return clean


def load_game_sql(game: str, query_type: str) -> str:
    """Reads '<game>_<query_type>.sql' template and formats target schema variables."""
    clean_game = validate_identifier(game)
    clean_type = validate_identifier(query_type)
    filename = f"{clean_game}_{clean_type}.sql"
    file_path = os.path.join(SQL_DIR, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target SQL template not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        raw_sql = f.read()

    table_name = f"cards_{clean_game}"
    return raw_sql.format(game=clean_game, table_name=table_name).strip()


def load_game_sql_statements(game: str, query_type: str) -> list[str]:
    """Splits multi-query SQL files into executable atomic statements, stripping comments."""
    formatted = load_game_sql(game=game, query_type=query_type)
    statements: list[str] = []
    for raw_chunk in formatted.split(";"):
        code_lines = [
            line.strip()
            for line in raw_chunk.strip().splitlines()
            if line.strip() and not line.strip().startswith("--")
        ]
        if code_lines:
            statements.append(raw_chunk.strip() + ";")
    return statements
