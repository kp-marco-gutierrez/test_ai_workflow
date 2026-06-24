import re
from pytest_bdd import when, then, scenarios, parsers

scenarios("../features/rename-a-list.feature")


@when(parsers.re(r'I rename the "(?P<list_name>[^"]+)" list to "(?P<new_name>[^"]*)"'))
def rename_list(page, list_name, new_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=re.compile(rf"^{re.escape(list_name)}$")),
    )
    rename_btn = column.locator(
        "button.rename-list, button.edit-list-name, [data-action='rename'], .rename-btn"
    )
    if rename_btn.count() > 0:
        rename_btn.first.click()
    else:
        column.locator(".column-header").dblclick()
    name_input = column.locator(
        "input.list-name-input, input.column-name-input, "
        "input[aria-label='List name'], input[aria-label='Column name']"
    ).first
    name_input.fill(new_name)
    name_input.press("Enter")


@then(parsers.parse('a column "{column_name}" is visible'))
def column_is_visible(page, column_name):
    headers = page.locator(".column-header")
    found = any(
        headers.nth(i).inner_text().strip() == column_name
        for i in range(headers.count())
    )
    assert found, f'Expected a column "{column_name}" to be visible'


@then(parsers.parse('a column "{column_name}" is not visible'))
def column_is_not_visible(page, column_name):
    headers = page.locator(".column-header")
    found = any(
        headers.nth(i).inner_text().strip() == column_name
        for i in range(headers.count())
    )
    assert not found, f'Expected no column "{column_name}" to be visible, but found one'
