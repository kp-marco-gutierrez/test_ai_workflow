from pytest_bdd import when, then, scenarios

scenarios("../features/board-layout-with-default-columns.feature")


@when("the board loads")
def board_loads(page):
    page.wait_for_load_state("domcontentloaded")


@then('the columns "To Do", "Doing", "Done" are visible in that order')
def check_columns_in_order(page):
    columns = page.locator(".column")
    assert columns.count() >= 3, (
        f'Expected at least 3 columns, found {columns.count()}'
    )
    expected = ["To Do", "Doing", "Done"]
    for i, name in enumerate(expected):
        col = columns.nth(i)
        assert col.is_visible(), f'Column "{name}" at position {i} is not visible'
        header = col.locator(".column-header, h2, h3").first
        actual = header.inner_text().strip()
        assert actual == name, (
            f'Expected column {i} to be "{name}", got "{actual}"'
        )


@then("each column shows 0 cards")
def check_columns_empty(page):
    columns = page.locator(".column")
    count = columns.count()
    assert count >= 3, f'Expected at least 3 columns, found {count}'
    for i in range(count):
        col = columns.nth(i)
        cards = col.locator(".card")
        card_count = cards.count()
        assert card_count == 0, (
            f'Column {i} expected 0 cards, found {card_count}'
        )


@then('the page heading is "Trello-lite"')
def check_page_heading(page):
    heading = page.locator("h1").first
    actual = heading.inner_text().strip()
    assert actual == "Trello-lite", (
        f'Expected page heading "Trello-lite", got "{actual}"'
    )
