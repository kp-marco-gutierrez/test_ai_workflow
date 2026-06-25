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
    # Verify the accent class produces a visually distinct computed style, not just a class name
    bg_color = header.evaluate("el => getComputedStyle(el).backgroundColor")
    border_top_color = header.evaluate("el => getComputedStyle(el).borderTopColor")
    transparent = {"rgba(0, 0, 0, 0)", "transparent", ""}
    assert bg_color not in transparent or border_top_color not in transparent, (
        f'Expected accent-{accent} class to produce a visible background or border color '
        f'on the "{column_name}" header, but styles appear transparent/default'
    )
