.PHONY: lint format typecheck deadcode security test check

CHECK_DIRS := src/database src/sql tests
SRC_DIRS   := src/database src/sql

lint:
	uv run ruff check $(CHECK_DIRS)
	uv run ruff format --check $(CHECK_DIRS)

format:
	uv run ruff check --fix $(CHECK_DIRS)
	uv run ruff format $(CHECK_DIRS)

typecheck:
	uv run mypy

deadcode:
	uv run vulture $(CHECK_DIRS) --min-confidence 80

security:
	uv run bandit -r $(SRC_DIRS) -ll

test:
	uv run pytest -s -v --color=yes --cov=src/database --cov=src/sql --cov-report=term-missing

check: lint typecheck deadcode security test