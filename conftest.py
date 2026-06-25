import os
import subprocess
import sys

import pytest
from playwright.sync_api import sync_playwright
from pytest_bdd import given, when, parsers


def pytest_configure(config):
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"],
        check=True,
    )


@pytest.fixture
def _browser():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        yield browser
        browser.close()


@given("the board app is open", target_fixture="page")
def board_app_open(_browser):
    index_html = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "index.html")
    )
    page = _browser.new_page()
    page.goto(f"file://{index_html}")
    return page


@given(parsers.parse('a card "{card_title}" is in the "{column_name}" column'))
def card_exists_in_column(page, card_title, column_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    card_input = column.locator("input.card-input, input[type='text']").first
    card_input.fill(card_title)
    add_button = column.locator("button.add-card, button[type='submit'], .add-card-btn").first
    add_button.click()
    card = column.locator(".card", has_text=card_title)
    assert card.count() > 0, (
        f'Setup failed: card "{card_title}" not found in "{column_name}" column after adding'
    )


# parsers.parse uses the `parse` library which requires at least one character
# for `{}` fields, so it cannot match empty strings.  These re-based steps
# cover only the empty-string cases without conflicting with the parsers.parse
# steps in the test files for non-empty values.
@given(parsers.parse('I move the card "{card_title}" up in the "{column_name}" column'))
def given_move_card_up(page, card_title, column_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    card = column.locator(".card", has_text=card_title).first
    move_up_button = card.locator(
        "button.move-up, button[data-action='move-up'], button:has-text('↑'), button:has-text('Up'), button[aria-label='Move up']"
    ).first
    move_up_button.click()


@when("I reload the page")
def reload_page_shared(page):
    page.reload()


@when(parsers.re(r'I rename the card "(?P<card_title>[^"]+)" to ""'))
def rename_card_to_empty(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    card_title_el = card.locator(".card-title, span, p").first
    card_title_el.dblclick()
    edit_input = card.locator("input.card-edit, input.rename-input, input[type='text']").first
    edit_input.fill("")
    edit_input.press("Enter")


@when(parsers.re(r'I add a card "" to the "(?P<column_name>[^"]+)" column'))
def add_empty_card_to_column(page, column_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    card_input = column.locator("input.card-input, input[type='text']").first
    card_input.fill("")
    add_button = column.locator("button.add-card, button[type='submit'], .add-card-btn").first
    add_button.click()
