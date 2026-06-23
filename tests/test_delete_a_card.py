import os
import pytest
from playwright.sync_api import sync_playwright
from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/delete-a-card.feature")


@pytest.fixture
def _browser():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        yield browser
        browser.close()


@given("the board app is open", target_fixture="page")
def board_app_open(_browser):
    index_html = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "index.html")
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


@when(parsers.parse('I delete the card "{card_title}"'))
def delete_card(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    delete_button = card.locator(
        "button.delete, button.delete-btn, button[data-action='delete'], button:has-text('Delete')"
    ).first
    delete_button.click()


@then(parsers.re(r'the "(?P<column_name>[^"]+)" column shows (?P<card_count>\d+) cards?'))
def column_shows_n_cards(page, column_name, card_count):
    expected = int(card_count)
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    cards = column.locator(".card")
    actual = cards.count()
    assert actual == expected, (
        f'Expected "{column_name}" column to show {expected} card(s), found {actual}'
    )


@then(parsers.parse('the "{column_name}" column contains a card titled "{card_title}"'))
def column_contains_card_titled(page, column_name, card_title):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    card = column.locator(".card", has_text=card_title)
    assert card.count() > 0, (
        f'Expected "{column_name}" column to contain a card titled "{card_title}"'
    )
