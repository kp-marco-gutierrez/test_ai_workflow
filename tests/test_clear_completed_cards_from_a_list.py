from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/clear-completed-cards-from-a-list.feature")


@given(parsers.parse('a completed card "{card_title}" is in the "{column_name}" column'))
def completed_card_in_column(page, card_title, column_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    card_input = column.locator("input.card-input, input[type='text']").first
    card_input.fill(card_title)
    add_button = column.locator("button.add-card, button[type='submit'], .add-card-btn").first
    add_button.click()
    card = column.locator(".card", has_text=card_title).first
    assert card.count() > 0, (
        f'Setup failed: card "{card_title}" not found in "{column_name}" column after adding'
    )
    checkbox = card.locator("input[type='checkbox'].complete-toggle, input[type='checkbox']").first
    if not checkbox.is_checked():
        checkbox.click()
    assert checkbox.is_checked(), (
        f'Setup failed: could not mark card "{card_title}" as complete'
    )


@when(parsers.parse('I clear completed cards from the "{column_name}" column'))
def clear_completed_cards(page, column_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    clear_btn = column.locator(
        "button.clear-completed, button[data-action='clear-completed'], "
        "button:has-text('Clear completed'), button:has-text('Clear Completed')"
    ).first
    clear_btn.click()


@then(parsers.parse('the card "{card_title}" is hidden'))
def card_is_hidden(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    assert not card.is_visible(), (
        f'Expected card "{card_title}" to be hidden but it was visible'
    )


@then(parsers.parse('the card "{card_title}" is visible'))
def card_is_visible(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    assert card.is_visible(), (
        f'Expected card "{card_title}" to be visible but it was not'
    )


@then(parsers.parse('the "{column_name}" column shows {count:d} card'))
def column_shows_n_cards(page, column_name, count):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    visible_cards = column.locator(".card").filter(has_text="").all()
    visible_count = sum(1 for c in visible_cards if c.is_visible())
    assert visible_count == count, (
        f'Expected "{column_name}" column to show {count} card(s), but found {visible_count}'
    )
