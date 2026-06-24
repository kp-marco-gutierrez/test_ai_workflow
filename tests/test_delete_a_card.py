from pytest_bdd import when, then, scenarios, parsers

scenarios("../features/delete-a-card.feature")


@when(parsers.parse('I delete the card "{card_title}"'))
def delete_card(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    delete_button = card.locator(
        "button.delete, button.delete-btn, button[data-action='delete'], button:has-text('Delete')"
    ).first
    delete_button.click()


@then(parsers.re(r'the "(?P<column_name>[^"]+)" column shows (?P<card_count>\d+) cards?'))
def column_shows_n_cards(page, column_name, card_count):
    expected = int(card_count)
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    cards = column.locator(".card")
    actual = cards.count()
    assert actual == expected, (
        f'Expected "{column_name}" column to show {expected} card(s), found {actual}'
    )


@then(parsers.parse('the "{column_name}" column contains a card titled "{card_title}"'))
def column_contains_card_titled(page, column_name, card_title):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    card = column.locator(".card", has_text=card_title)
    assert card.count() > 0, (
        f'Expected "{column_name}" column to contain a card titled "{card_title}"'
    )
