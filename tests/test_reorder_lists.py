from pytest_bdd import when, then, scenarios, parsers

scenarios("../features/reorder-lists.feature")


@when(parsers.parse('I move the "{list_name}" list left'))
def move_list_left(page, list_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=list_name),
    )
    move_left_button = column.locator(
        "button.move-left, button[data-action='move-left'], button:has-text('←'), "
        "button:has-text('Left'), button[aria-label='Move list left']"
    ).first
    move_left_button.click()


@when(parsers.parse('I move the "{list_name}" list right'))
def move_list_right(page, list_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=list_name),
    )
    move_right_button = column.locator(
        "button.move-right, button[data-action='move-right'], button:has-text('→'), "
        "button:has-text('Right'), button[aria-label='Move list right']"
    ).first
    move_right_button.click()


@then(parsers.parse('the board lists "{first_list}" before "{second_list}"'))
def board_lists_before(page, first_list, second_list):
    columns = page.locator(".column")
    count = columns.count()
    headers = [
        columns.nth(i).locator(".column-header").inner_text() for i in range(count)
    ]
    first_indices = [i for i, h in enumerate(headers) if first_list in h]
    second_indices = [i for i, h in enumerate(headers) if second_list in h]
    assert first_indices, f'List "{first_list}" not found on the board'
    assert second_indices, f'List "{second_list}" not found on the board'
    assert first_indices[0] < second_indices[0], (
        f'Expected list "{first_list}" (index {first_indices[0]}) to appear before '
        f'"{second_list}" (index {second_indices[0]}) on the board'
    )
