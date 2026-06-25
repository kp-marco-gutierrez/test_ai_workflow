"""
Pytest support for the tests/ directory.

Patches ``sync_playwright`` so that each new call automatically stops any
previously-started playwright context before starting a fresh one.

Background: playwright's sync API uses greenlets, meaning the asyncio event
loop runs on the main thread in a shared greenlet context.  When a pytest-bdd
Given step starts playwright via ``.start()`` and never calls ``.stop()``,
the loop remains "running" (from Python's perspective) for the lifetime of
that greenlet.  If a subsequent test tries to create a new playwright context,
``asyncio.get_running_loop()`` returns the still-live loop and playwright
raises:

    "It looks like you are using Playwright Sync API inside the asyncio loop."

The wrapper below ensures at most one playwright context is live at a time.
The ``_playwright_teardown`` autouse fixture stops any orphaned context at the
END of each test (during teardown), which gives the event loop time to fully
unwind before the next test's setup creates a fresh context.  Only contexts
started via ``.start()`` (without a context-manager ``__exit__``) are stopped
this way; contexts owned by the ``_browser`` fixture are left to their own
teardown.
"""
import sys

import pytest


# Module-level state so the autouse teardown fixture can access it.
# ``via_start`` is True only when playwright was opened with .start() rather
# than via the ``with sync_playwright() as pw:`` context manager — that is the
# only case where there is no matching __exit__ to clean up.
_playwright_state = {"active": None, "via_start": False}


def _make_safe_sync_playwright(original_factory):
    """
    Return a replacement for ``sync_playwright`` that stops any still-live
    playwright context before starting a new one.
    """
    class _Managed:
        def __init__(self):
            # Stop the previously-active context, if any
            if _playwright_state["active"] is not None:
                try:
                    _playwright_state["active"].stop()
                except Exception:
                    pass
                _playwright_state["active"] = None
                _playwright_state["via_start"] = False
            self._cm = original_factory()

        def start(self):
            result = self._cm.start()
            _playwright_state["active"] = result
            _playwright_state["via_start"] = True
            return result

        def __enter__(self):
            result = self._cm.__enter__()
            _playwright_state["active"] = result
            _playwright_state["via_start"] = False
            return result

        def __exit__(self, *args):
            try:
                result = self._cm.__exit__(*args)
            except Exception:
                result = False
            _playwright_state["active"] = None
            _playwright_state["via_start"] = False
            return result

    def managed_sync_playwright():
        return _Managed()

    return managed_sync_playwright


@pytest.fixture(autouse=True)
def _playwright_teardown():
    """
    Stop any playwright context that was opened via ``.start()`` (without a
    context-manager ``__exit__``) during this test.  Running the stop inside
    teardown — rather than deferring it to the start of the *next* test —
    gives the event loop time to fully unwind before the next fixture setup
    tries to create a fresh playwright context.

    Contexts owned by the ``_browser`` fixture (opened via the context manager)
    are NOT touched here; they have their own teardown via ``__exit__``.
    """
    yield
    if _playwright_state["active"] is not None and _playwright_state.get("via_start"):
        try:
            _playwright_state["active"].stop()
        except Exception:
            pass
        _playwright_state["active"] = None
        _playwright_state["via_start"] = False


def pytest_configure(config):
    """Patch sync_playwright globally before any test modules are imported."""
    import playwright.sync_api as pw_api
    from playwright.sync_api import sync_playwright as original

    safe = _make_safe_sync_playwright(original)

    # Patch the playwright module so all subsequent imports get the safe version
    pw_api.sync_playwright = safe

    # Root conftest.py is already imported at this point — patch its local binding
    root_conftest = sys.modules.get("conftest")
    if root_conftest is not None and hasattr(root_conftest, "sync_playwright"):
        root_conftest.sync_playwright = safe
