import pytest

from src.sql.sql_loader import (
    load_game_sql,
    load_game_sql_statements,
    validate_identifier,
)


def test_validate_identifier_success():
    """Verifies normalization and acceptance of compliant alphanumeric identifiers."""
    assert validate_identifier("berserk") == "berserk"
    assert validate_identifier("  CARDS_table_123 ") == "cards_table_123"


@pytest.mark.parametrize(
    "invalid_id",
    [
        "berserk; DROP TABLE users;",
        "berserk/../indices",
        "table-name",
        "cards*",
        "   ",
    ],
)
def test_validate_identifier_failures(invalid_id):
    """Ensures SQL injection payloads and path traversal vectors are aggressively rejected."""
    with pytest.raises(ValueError, match="Invalid alphanumeric identifier"):
        validate_identifier(invalid_id)


def test_load_game_sql_templating():
    """Validates dynamic interpolation of game and table_name placeholders in SQL templates."""
    sql = load_game_sql("berserk", "schema")
    assert "CREATE TABLE IF NOT EXISTS cards_berserk" in sql, (
        "Target table DDL header missing after interpolation"
    )
    assert "faiss_id INTEGER PRIMARY KEY" in sql, (
        "Primary vector index column missing from schema definition"
    )
    assert "{table_name}" not in sql, (
        "Unresolved template placeholder leaked into final SQL payload"
    )


def test_load_game_sql_missing_file():
    """Confirms requesting a non-existent SQL template raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Target SQL template not found"):
        load_game_sql("unknown_game_999", "schema")


def test_load_game_sql_statements_parsing():
    """Verifies multi-statement splitting and comment stripping across composite SQL scripts."""
    statements = load_game_sql_statements("berserk", "indices")
    assert len(statements) == 3, (
        f"Expected 3 atomic index statements, parsed {len(statements)}"
    )
    for stmt in statements:
        assert "CREATE INDEX IF NOT EXISTS" in stmt, (
            f"Malformed index DDL statement: {stmt}"
        )
        assert stmt.endswith(";"), "Atomic SQL statement lacks terminating semicolon"
