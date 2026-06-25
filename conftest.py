import os
import subprocess
import sys

import pytest
from playwright.sync_api import sync_playwright
from pytest_bdd import given, when, then, parsers


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


@when(parsers.parse('I add a card "{card_title}" to the "{column_name}" column'))
def add_card_to_column(page, card_title, column_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    card_input = column.locator("input.card-input, input[type='text']").first
    card_input.fill(card_title)
    add_button = column.locator("button.add-card, button[type='submit'], .add-card-btn").first
    add_button.click()


@when(parsers.parse('I add a "{color}" label to the card "{card_title}"'))
def add_label_to_card(page, color, card_title):
    card = page.locator(".card", has_text=card_title).first
    open_btn = card.locator(
        "button.label, button.add-label, button[data-action='label'], "
        "button:has-text('Label'), .label-btn"
    )
    open_btn.first.click()
    color_option = page.locator(
        f".label-picker [data-color='{color}'], "
        f".label-picker .label-{color}, "
        f".dropdown [data-color='{color}'], "
        f".popover [data-color='{color}'], "
        f"[role='menu'] [data-color='{color}']"
    )
    color_option.first.wait_for(state="visible", timeout=5000)
    color_option.first.click()


@when(parsers.parse('I set the due date of the card "{card_title}" to "{due_date}"'))
def set_due_date(page, card_title, due_date):
    card = page.locator(".card", has_text=card_title).first
    date_input = card.locator("input[type='date']")
    if date_input.count() > 0:
        date_input.first.fill(due_date)
        date_input.first.press("Tab")
    else:
        card.click()
        detail = page.locator(".card-modal, .card-detail, .modal, [role='dialog']")
        detail.wait_for(state="visible", timeout=5000)
        date_field = detail.locator(
            "input[type='date'].due-date, input[type='date'], input.due-date"
        ).first
        date_field.fill(due_date)
        save_button = detail.locator(
            "button.save, button.save-due-date, button[data-action='save'], button:has-text('Save')"
        )
        if save_button.count() > 0:
            save_button.first.click()
        else:
            date_field.press("Enter")
        close_button = detail.locator(
            "button.close, button[data-action='close'], button:has-text('Close'), button:has-text('×')"
        )
        if close_button.count() > 0:
            close_button.first.click()


@when(parsers.parse('I move the card "{card_title}" to the "{target_column}" column'))
def move_card_to_column(page, card_title, target_column):
    card = page.locator(".card", has_text=card_title).first
    move_select = card.locator("select")
    move_select.select_option(label=target_column)


@then(parsers.parse('the "{column_name}" column lists "{first_card}" before "{second_card}"'))
def column_lists_card_before_other_shared(page, column_name, first_card, second_card):
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
