from pytest_bdd import when, then, scenarios, parsers

scenarios("../features/drag-a-card-to-another-column.feature")


@when(parsers.parse('I drag the card "{card_title}" onto the "{target_column}" column'))
def drag_card_onto_column(page, card_title, target_column):
    card = page.locator(".card", has_text=card_title).first
    target = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=target_column),
    )
    card.drag_to(target)


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
