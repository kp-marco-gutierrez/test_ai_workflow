from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/set-a-due-date-on-a-card.feature")


@given(parsers.parse('the card "{card_title}" has the due date "{due_date}"'))
def card_has_due_date(page, card_title, due_date):
    card = page.locator(".card", has_text=card_title).first
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


@when(parsers.parse('I set the due date of the card "{card_title}" to "{due_date}"'))
def set_due_date(page, card_title, due_date):
    card = page.locator(".card", has_text=card_title).first
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


@when(parsers.parse('I clear the due date of the card "{card_title}"'))
def clear_due_date(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    date_input = card.locator("input[type='date']")
    if date_input.count() > 0:
        date_input.first.fill("")
        date_input.first.press("Tab")
    else:
        card.click()
        detail = page.locator(".card-modal, .card-detail, .modal, [role='dialog']")
        detail.wait_for(state="visible", timeout=5000)
        date_field = detail.locator("input[type='date'].due-date, input[type='date'], input.due-date").first
        date_field.fill("")
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


@then(parsers.parse('the card "{card_title}" shows the due date "{due_date}"'))
def card_shows_due_date(page, card_title, due_date):
    card = page.locator(".card", has_text=card_title).first
    date_input = card.locator("input[type='date']")
    if date_input.count() > 0:
        actual = date_input.first.input_value()
        assert actual == due_date, f'Expected due date "{due_date}", got "{actual}"'
        return
    due_date_el = card.locator(".due-date, .card-due-date, [data-field='due-date'], [class*='due']")
    if due_date_el.count() > 0:
        actual = due_date_el.first.inner_text()
        assert due_date in actual, (
            f'Expected due date "{due_date}" visible on card "{card_title}", got "{actual}"'
        )
        return
    # Fall back to checking the modal
    card.click()
    detail = page.locator(".card-modal, .card-detail, .modal, [role='dialog']")
    detail.wait_for(state="visible", timeout=5000)
    date_field = detail.locator("input[type='date']").first
    actual = date_field.input_value()
    assert actual == due_date, f'Expected due date "{due_date}", got "{actual}"'


@then(parsers.parse('the card "{card_title}" shows no due date'))
def card_shows_no_due_date(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    date_input = card.locator("input[type='date']")
    if date_input.count() > 0:
        actual = date_input.first.input_value()
        assert actual == "", f'Expected no due date on card "{card_title}", got "{actual}"'
        return
    due_date_el = card.locator(
        ".due-date, .card-due-date, [data-field='due-date'], [class*='due']"
    ).filter(has_text=True)
    assert due_date_el.count() == 0, (
        f'Expected no due date on card "{card_title}", but found one'
    )
