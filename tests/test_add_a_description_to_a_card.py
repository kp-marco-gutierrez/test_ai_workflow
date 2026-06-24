from pytest_bdd import when, then, scenarios, parsers

scenarios("../features/add-a-description-to-a-card.feature")


@when(parsers.parse('I open the card "{card_title}"'))
def open_card(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    open_button = card.locator(
        "button.open-card, button.card-open, button[data-action='open'], button:has-text('Open')"
    )
    if open_button.count() > 0:
        open_button.first.click()
    else:
        card.click()
    detail = page.locator(".card-modal, .card-detail, .modal, [role='dialog']")
    detail.wait_for(state="visible", timeout=5000)


@when(parsers.parse('I set the description to "{description}"'))
def set_description(page, description):
    detail = page.locator(".card-modal, .card-detail, .modal, [role='dialog']").first
    desc_field = detail.locator(
        "textarea.card-description, textarea.description, textarea, input.description, [data-field='description']"
    ).first
    desc_field.fill(description)
    save_button = detail.locator(
        "button.save, button.save-description, button[data-action='save'], button:has-text('Save')"
    )
    if save_button.count() > 0:
        save_button.first.click()
    else:
        desc_field.press("Tab")


@then(parsers.parse('the card "{card_title}" shows the description "{description}"'))
def card_shows_description(page, card_title, description):
    detail = page.locator(".card-modal, .card-detail, .modal, [role='dialog']").first
    if detail.is_visible():
        desc_field = detail.locator(
            "textarea.card-description, textarea.description, textarea, input.description, [data-field='description']"
        ).first
        actual = desc_field.input_value() if desc_field.evaluate("el => el.tagName").lower() in ("input", "textarea") else desc_field.inner_text()
        assert actual == description, (
            f'Expected description "{description}", got "{actual}"'
        )
    else:
        card = page.locator(".card", has_text=card_title).first
        desc_el = card.locator(".card-description, .description, [data-field='description']").first
        assert desc_el.is_visible(), f'No description element found on card "{card_title}"'
        assert desc_el.inner_text() == description, (
            f'Expected description "{description}", got "{desc_el.inner_text()}"'
        )


@then(parsers.parse('the card "{card_title}" shows no description'))
def card_shows_no_description(page, card_title):
    detail = page.locator(".card-modal, .card-detail, .modal, [role='dialog']").first
    if detail.is_visible():
        desc_field = detail.locator(
            "textarea.card-description, textarea.description, textarea, input.description, [data-field='description']"
        ).first
        if desc_field.count() > 0:
            actual = desc_field.input_value() if desc_field.evaluate("el => el.tagName").lower() in ("input", "textarea") else desc_field.inner_text()
            assert actual == "", (
                f'Expected empty description, got "{actual}"'
            )
    else:
        card = page.locator(".card", has_text=card_title).first
        desc_el = card.locator(".card-description, .description, [data-field='description']")
        visible_desc = desc_el.filter(has_text=True)
        assert visible_desc.count() == 0, (
            f'Expected no description on card "{card_title}", but found one'
        )
