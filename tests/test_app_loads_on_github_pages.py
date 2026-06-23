import os
import pytest
from pytest_bdd import given, when, then, scenarios

scenarios("../features/app-loads-on-github-pages.feature")


@pytest.fixture
def _browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        yield browser
        browser.close()


@given("the app page is open", target_fixture="page")
def app_page_open(_browser):
    index_html = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "index.html")
    )
    page = _browser.new_page()
    page.goto(f"file://{index_html}")
    return page


@when("the page loads")
def page_loads(page):
    page.wait_for_load_state("domcontentloaded")


@then('the document title is "Trello-lite"')
def check_document_title(page):
    assert page.title() == "Trello-lite", (
        f'Expected document title "Trello-lite", got "{page.title()}"'
    )


@then('the heading "Trello-lite" is visible')
def check_heading_visible(page):
    heading = page.locator("h1", has_text="Trello-lite")
    assert heading.is_visible(), 'Expected heading "Trello-lite" to be visible'


@then("a board container is visible")
def check_board_container_visible(page):
    container = page.locator(".board-container")
    assert container.is_visible(), "Expected .board-container to be visible"
