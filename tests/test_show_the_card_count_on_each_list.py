from pytest_bdd import when, then, scenarios, parsers

scenarios("../features/show-the-card-count-on-each-list.feature")


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


@when(parsers.parse('I delete the card "{card_title}"'))
def delete_card(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    delete_button = card.locator(
        "button.delete, button.delete-btn, button[data-action='delete'], button:has-text('Delete')"
    ).first
    delete_button.click()


@then(parsers.re(r'the "(?P<column_name>[^"]+)" column header shows a count of (?P<count>\d+)'))
def column_header_shows_count(page, column_name, count):
    expected = int(count)
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    header = column.locator(".column-header").first
    count_el = header.locator(".card-count, .count, [data-count]").first
    count_el.wait_for(state="visible")
    actual_text = count_el.inner_text().strip()
    assert str(expected) in actual_text, (
        f'Expected "{column_name}" column header to show count {expected}, '
        f'but found: "{actual_text}"'
    )
