import os
import pytest
from playwright.sync_api import sync_playwright
from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/delete-a-list.feature")


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


@when(parsers.parse('I delete the "{list_name}" list'))
def delete_list(page, list_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=list_name),
    )
    delete_button = column.locator(
        "button.delete-list, button.delete-column, [aria-label='Delete list'],"
        " [aria-label='Delete column'], button[data-action='delete']"
    ).first
    delete_button.click()


@then(parsers.parse('a column "{column_name}" is not visible'))
def column_is_not_visible(page, column_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    assert column.count() == 0, (
        f'Expected column "{column_name}" to be removed from the board, but it is still visible'
    )


@then(parsers.re(r"the board shows (?P<count>\d+) columns?"))
def board_shows_n_columns(page, count):
    expected = int(count)
    columns = page.locator(".column")
    actual = columns.count()
    assert actual == expected, (
        f"Expected board to show {expected} column(s), found {actual}"
    )


@then(parsers.parse('no card titled "{card_title}" is visible'))
def no_card_titled_is_visible(page, card_title):
    card = page.locator(".card", has_text=card_title)
    assert card.count() == 0, (
        f'Expected no card titled "{card_title}" to be visible, but found {card.count()}'
    )
