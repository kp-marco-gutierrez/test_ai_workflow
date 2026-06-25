from pytest_bdd import when, then, scenarios, parsers

scenarios("../features/plan-and-track-a-task-end-to-end.feature")


@when("I reload the page")
def reload_the_page(page):
    page.reload()
    page.wait_for_load_state("load")


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


@then(parsers.parse('the card "{card_title}" has a "{color}" label'))
def card_has_color_label(page, card_title, color):
    card = page.locator(".card", has_text=card_title).first
    label = card.locator(
        f".label-{color}, [data-color='{color}'], .label[data-color='{color}']"
    )
    assert label.count() > 0, (
        f'Expected card "{card_title}" to have a "{color}" label, but none found'
    )
    assert label.first.is_visible(), (
        f'Expected "{color}" label on card "{card_title}" to be visible'
    )


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
    card.click()
    detail = page.locator(".card-modal, .card-detail, .modal, [role='dialog']")
    detail.wait_for(state="visible", timeout=5000)
    date_field = detail.locator("input[type='date']").first
    actual = date_field.input_value()
    assert actual == due_date, f'Expected due date "{due_date}", got "{actual}"'
