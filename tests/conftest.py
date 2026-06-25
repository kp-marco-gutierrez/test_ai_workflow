"""
Pytest support for the tests/ directory.

Patches ``sync_playwright`` so that each new call automatically stops any
previously-started playwright context before starting a fresh one.

Background: playwright's sync API uses greenlets, meaning the asyncio event
loop runs on the main thread in a separate greenlet.  When a pytest-bdd
Background step starts playwright via ``.start()`` and never calls ``.stop()``,
the loop remains "running" (from Python's perspective) for the lifetime of
that greenlet.  If a second ``.start()`` call is made in the same test (e.g.,
from a Scenario-level Given step that also sets target_fixture="page"), or in
any subsequent test, ``asyncio.get_running_loop()`` returns the still-live
loop and playwright raises:

    "It looks like you are using Playwright Sync API inside the asyncio loop."

The wrapper below ensures at most one playwright context is live at a time.
"""
import sys

import pytest


def _make_safe_sync_playwright(original_factory):
    """
    Return a replacement for ``sync_playwright`` that stops any still-live
    playwright context before starting a new one.
    """
    _state = {"active": None}

    class _Managed:
        def __init__(self):
            # Stop the previously-active context, if any
            if _state["active"] is not None:
                try:
                    _state["active"].stop()
                except Exception:
                    pass
                _state["active"] = None
            self._cm = original_factory()

        def start(self):
            result = self._cm.start()
            _state["active"] = result
            return result

        def __enter__(self):
            result = self._cm.__enter__()
            _state["active"] = result
            return result

        def __exit__(self, *args):
            try:
                result = self._cm.__exit__(*args)
            except Exception:
                result = False
            _state["active"] = None
            return result

    def managed_sync_playwright():
        return _Managed()

    return managed_sync_playwright


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
