import pytest
from playwright.sync_api import expect

# Give the demo site a little headroom on slow connections.
# Assertions still retry until this timeout, so no fixed sleeps are needed.
expect.set_options(timeout=10_000)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Use a fixed desktop viewport so layout is the same on every machine."""
    return {**browser_context_args, "viewport": {"width": 1280, "height": 800}}
