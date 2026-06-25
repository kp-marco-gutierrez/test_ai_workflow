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


@then(parsers.parse('the card "{card_title}" is marked overdue'))
def card_is_marked_overdue(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    card.wait_for(state="visible", timeout=5000)
    # The card must carry an overdue indicator — either a CSS class or a data attribute
    overdue_class = card.evaluate(
        "el => el.classList.contains('overdue') || el.classList.contains('past-due') || "
        "el.getAttribute('data-overdue') === 'true' || "
        "el.querySelector('.overdue, .past-due, [data-overdue]') !== null"
    )
    assert overdue_class, (
        f'Expected card "{card_title}" to be marked overdue, but no overdue indicator was found'
    )


@then(parsers.parse('the card "{card_title}" is not marked overdue'))
def card_is_not_marked_overdue(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    card.wait_for(state="visible", timeout=5000)
    overdue_class = card.evaluate(
        "el => el.classList.contains('overdue') || el.classList.contains('past-due') || "
        "el.getAttribute('data-overdue') === 'true' || "
        "el.querySelector('.overdue, .past-due, [data-overdue]') !== null"
    )
    assert not overdue_class, (
        f'Expected card "{card_title}" to NOT be marked overdue, but an overdue indicator was found'
    )
