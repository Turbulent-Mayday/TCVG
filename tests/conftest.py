import os
from unittest.mock import patch

import pytest


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    """Captures test execution status across setup, call, and teardown phases."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture
def card_preview(request):
    """Renders registered card arrays only after the test passes and status is logged."""
    queue = []
    yield queue.append

    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.passed:
        for card_array in queue:
            from tests.test_image_generator import render_card_to_terminal

            render_card_to_terminal(card_array)


@pytest.fixture(autouse=True)
def setup_test_env(tmp_path):
    """Automatically sandboxes the runtime environment for every test invocation."""
    test_db_file = tmp_path / "test_berserk.db"
    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": f"://{test_db_file}",
            "DATABASE_AUTH_TOKEN": "test_token_mog",
            "SUPPORTED_GAMES": "berserk",
        },
    ):
        yield
