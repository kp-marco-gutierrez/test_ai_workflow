from pytest_bdd import when, then, scenarios, parsers

scenarios("../features/delete-a-list.feature")


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
