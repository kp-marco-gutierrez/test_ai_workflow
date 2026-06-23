import os
import pytest
from playwright.sync_api import sync_playwright
from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/reorder-cards-within-a-list.feature")


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


@when(parsers.parse('I move the card "{card_title}" up in the "{column_name}" column'))
def move_card_up(page, card_title, column_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    card = column.locator(".card", has_text=card_title).first
    move_up_button = card.locator(
        "button.move-up, button[data-action='move-up'], button:has-text('↑'), button:has-text('Up'), button[aria-label='Move up']"
    ).first
    move_up_button.click()


@when(parsers.parse('I move the card "{card_title}" down in the "{column_name}" column'))
def move_card_down(page, card_title, column_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    card = column.locator(".card", has_text=card_title).first
    move_down_button = card.locator(
        "button.move-down, button[data-action='move-down'], button:has-text('↓'), button:has-text('Down'), button[aria-label='Move down']"
    ).first
    move_down_button.click()


@then(parsers.parse('the "{column_name}" column lists "{first_card}" before "{second_card}"'))
def column_lists_card_before_other(page, column_name, first_card, second_card):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    cards = column.locator(".card")
    count = cards.count()
    titles = [cards.nth(i).inner_text() for i in range(count)]
    first_indices = [i for i, t in enumerate(titles) if first_card in t]
    second_indices = [i for i, t in enumerate(titles) if second_card in t]
    assert first_indices, f'Card "{first_card}" not found in "{column_name}" column'
    assert second_indices, f'Card "{second_card}" not found in "{column_name}" column'
    assert first_indices[0] < second_indices[0], (
        f'Expected "{first_card}" (index {first_indices[0]}) to appear before '
        f'"{second_card}" (index {second_indices[0]}) in "{column_name}" column'
    )
