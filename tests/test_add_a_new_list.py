from pytest_bdd import when, then, scenarios, parsers

scenarios("../features/add-a-new-list.feature")


@when(parsers.re(r'I add a list named "(?P<list_name>.+)"'))
def add_list_named(page, list_name):
    list_input = page.locator("input.list-input, input.add-list-input, input[placeholder*='list' i]").first
    list_input.fill(list_name)
    add_button = page.locator("button.add-list, button.add-list-btn, button[data-action='add-list']").first
    add_button.click()


@when(parsers.re(r'I add a list named ""'))
def add_list_named_empty(page):
    list_input = page.locator("input.list-input, input.add-list-input, input[placeholder*='list' i]").first
    list_input.fill("")
    add_button = page.locator("button.add-list, button.add-list-btn, button[data-action='add-list']").first
    add_button.click()


@then(parsers.parse('a column "{column_name}" is visible'))
def column_is_visible(page, column_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    assert column.count() > 0, (
        f'Expected a column named "{column_name}" to be visible on the board'
    )


@then(parsers.re(r'the board shows (?P<column_count>\d+) columns?'))
def board_shows_n_columns(page, column_count):
    expected = int(column_count)
    columns = page.locator(".column")
    actual = columns.count()
    assert actual == expected, (
        f'Expected board to show {expected} column(s), found {actual}'
    )


@then(parsers.parse('an error "{error_message}" is shown'))
def error_is_shown(page, error_message):
    error = page.locator(
        ".error, .error-message, [role='alert']",
        has_text=error_message,
    )
    assert error.count() > 0, (
        f'Expected error "{error_message}" to be visible on the page'
    )
