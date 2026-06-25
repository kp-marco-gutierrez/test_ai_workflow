from pytest_bdd import when, then, scenarios, parsers

scenarios("../features/placeholder-for-empty-lists.feature")


@when("the board loads")
def board_loads(page):
    page.wait_for_load_state("domcontentloaded")


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


@then(parsers.parse('the "{column_name}" column shows the placeholder "{placeholder_text}"'))
def column_shows_placeholder(page, column_name, placeholder_text):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    placeholder = column.locator(
        ".empty-placeholder, .placeholder, [data-placeholder], .no-cards",
        has_text=placeholder_text,
    )
    assert placeholder.count() > 0 and placeholder.first.is_visible(), (
        f'Expected "{column_name}" column to show placeholder "{placeholder_text}"'
    )


@then(parsers.parse('the "{column_name}" column does not show the placeholder "{placeholder_text}"'))
def column_does_not_show_placeholder(page, column_name, placeholder_text):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    placeholder = column.locator(
        ".empty-placeholder, .placeholder, [data-placeholder], .no-cards",
        has_text=placeholder_text,
    )
    visible_count = sum(1 for i in range(placeholder.count()) if placeholder.nth(i).is_visible())
    assert visible_count == 0, (
        f'Expected "{column_name}" column to NOT show placeholder "{placeholder_text}", but it was visible'
    )
