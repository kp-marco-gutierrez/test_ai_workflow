from pytest_bdd import when, then, parsers, scenarios

scenarios("../features/color-coded-column-headers.feature")


@when("the board loads")
def board_loads(page):
    page.wait_for_load_state("domcontentloaded")


@then(parsers.parse('the "{column_name}" column header has the accent "{accent}"'))
def column_header_has_accent(page, column_name, accent):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    header = column.locator(".column-header").first
    classes = header.get_attribute("class") or ""
    assert f"accent-{accent}" in classes, (
        f'Expected "{column_name}" column header to have class "accent-{accent}", '
        f'but got classes: "{classes}"'
    )
