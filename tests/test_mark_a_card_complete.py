from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/mark-a-card-complete.feature")


@given(parsers.parse('the card "{card_title}" is complete'))
def card_is_complete(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    checkbox = card.locator("input[type='checkbox'].complete-toggle, input[type='checkbox']").first
    if not checkbox.is_checked():
        checkbox.click()
    assert checkbox.is_checked(), (
        f'Setup failed: card "{card_title}" could not be marked complete'
    )


@when(parsers.parse('I mark the card "{card_title}" complete'))
def mark_card_complete(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    checkbox = card.locator("input[type='checkbox'].complete-toggle, input[type='checkbox']").first
    assert not checkbox.is_checked(), (
        f'Expected card "{card_title}" to be not complete before marking it complete'
    )
    checkbox.click()


@when(parsers.parse('I mark the card "{card_title}" not complete'))
def mark_card_not_complete(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    checkbox = card.locator("input[type='checkbox'].complete-toggle, input[type='checkbox']").first
    assert checkbox.is_checked(), (
        f'Expected card "{card_title}" to be complete before unmarking it'
    )
    checkbox.click()


@then(parsers.parse('the card "{card_title}" is shown as complete'))
def card_shown_as_complete(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    checkbox = card.locator("input[type='checkbox'].complete-toggle, input[type='checkbox']").first
    assert checkbox.is_checked(), (
        f'Expected card "{card_title}" checkbox to be checked (complete)'
    )
    # The card must also have a visual indicator of completion (class or attribute)
    card_classes = card.get_attribute("class") or ""
    assert "complete" in card_classes or "done" in card_classes, (
        f'Expected card "{card_title}" to have a "complete" or "done" CSS class, got: "{card_classes}"'
    )


@then(parsers.parse('the card "{card_title}" is shown as not complete'))
def card_shown_as_not_complete(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    checkbox = card.locator("input[type='checkbox'].complete-toggle, input[type='checkbox']").first
    assert not checkbox.is_checked(), (
        f'Expected card "{card_title}" checkbox to be unchecked (not complete)'
    )
    card_classes = card.get_attribute("class") or ""
    assert "complete" not in card_classes and "done" not in card_classes, (
        f'Expected card "{card_title}" to not have "complete" or "done" CSS class, got: "{card_classes}"'
    )
