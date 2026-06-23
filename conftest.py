import subprocess
import sys

from pytest_bdd import when, parsers


def pytest_configure(config):
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"],
        check=True,
    )


# parsers.parse uses the `parse` library which requires at least one character
# for `{}` fields, so it cannot match an empty card title "".  This re-based
# step covers only that empty-string case; it will not conflict with the
# parsers.parse step in the test file for non-empty titles.
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
