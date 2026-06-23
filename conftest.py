import subprocess
import sys

from pytest_bdd import when, parsers


def pytest_configure(config):
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"],
        check=True,
    )


# parsers.parse uses the `parse` library which requires at least one character
# for `{}` fields, so it cannot match empty strings.  These re-based steps
# cover only the empty-string cases without conflicting with the parsers.parse
# steps in the test files for non-empty values.
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
