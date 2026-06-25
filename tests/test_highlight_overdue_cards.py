from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/highlight-overdue-cards.feature")


@given(parsers.parse('a card "{card_title}" with due date "{due_date}" is in the "{column_name}" column'))
def card_with_due_date_in_column(page, card_title, due_date, column_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    card_input = column.locator("input.card-input, input[type='text']").first
    card_input.fill(card_title)
    add_button = column.locator("button.add-card, button[type='submit'], .add-card-btn").first
    add_button.click()
    card = column.locator(".card", has_text=card_title).first
    # Set the due date on the card
    date_input = card.locator("input[type='date']")
    if date_input.count() > 0:
        date_input.first.fill(due_date)
        date_input.first.press("Tab")
    else:
        card.click()
        detail = page.locator(".card-modal, .card-detail, .modal, [role='dialog']")
        detail.wait_for(state="visible", timeout=5000)
        date_field = detail.locator("input[type='date'].due-date, input[type='date'], input.due-date").first
        date_field.fill(due_date)
        save_button = detail.locator(
            "button.save, button.save-due-date, button[data-action='save'], button:has-text('Save')"
        )
        if save_button.count() > 0:
            save_button.first.click()
        else:
            date_field.press("Enter")
        close_button = detail.locator(
            "button.close, button[data-action='close'], button:has-text('Close'), button:has-text('×')"
        )
        if close_button.count() > 0:
            close_button.first.click()


@when("the board loads")
def board_loads(page):
    page.reload()
    page.wait_for_load_state("networkidle")


@then(parsers.parse('the card "{card_title}" has the "{css_class}" CSS class'))
def card_has_css_class(page, card_title, css_class):
    card = page.locator(".card", has_text=card_title).first
    card.wait_for(state="visible", timeout=5000)
    has_class = card.evaluate(f"el => el.classList.contains('{css_class}')")
    assert has_class, (
        f'Expected card "{card_title}" to have CSS class "{css_class}", but it was absent'
    )


@then(parsers.parse('the card "{card_title}" is visible and does not have the "{css_class}" CSS class'))
def card_is_visible_without_css_class(page, card_title, css_class):
    card = page.locator(".card", has_text=card_title).first
    card.wait_for(state="visible", timeout=5000)
    assert card.is_visible(), f'Expected card "{card_title}" to be visible'
    has_class = card.evaluate(f"el => el.classList.contains('{css_class}')")
    assert not has_class, (
        f'Expected card "{card_title}" to NOT have CSS class "{css_class}", but it was present'
    )
