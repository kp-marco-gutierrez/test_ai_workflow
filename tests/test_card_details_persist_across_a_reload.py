from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/card-details-persist-across-a-reload.feature")


# ── Given: label ─────────────────────────────────────────────────────────────

@given(parsers.parse('the card "{card_title}" has a "{color}" label'))
def card_has_label(page, card_title, color):
    card = page.locator(".card", has_text=card_title).first
    label_btn = card.locator(
        f"button.label-{color}, button[data-label='{color}'], "
        f".label-{color}, [data-color='{color}'], button:has-text('{color}')"
    )
    if label_btn.count() > 0:
        label_btn.first.click()
    else:
        open_btn = card.locator(
            "button.label, button.add-label, button[data-action='label'], "
            "button:has-text('Label'), .label-btn"
        )
        open_btn.first.click()
        color_option = page.locator(
            f".label-picker [data-color='{color}'], "
            f".label-picker .label-{color}, "
            f".dropdown [data-color='{color}'], "
            f".popover [data-color='{color}'], "
            f"[role='menu'] [data-color='{color}']"
        )
        color_option.first.click()
    label_indicator = card.locator(
        f".label-{color}, [data-color='{color}'], .label[data-color='{color}']"
    )
    assert label_indicator.count() > 0, (
        f'Setup failed: "{color}" label not found on card "{card_title}" after adding'
    )


# ── Given: due date ───────────────────────────────────────────────────────────

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
        date_field = detail.locator(
            "input[type='date'].due-date, input[type='date'], input.due-date"
        ).first
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


# ── Given: completion ─────────────────────────────────────────────────────────

@given(parsers.parse('the card "{card_title}" is complete'))
def card_is_complete(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    checkbox = card.locator(
        "input[type='checkbox'].complete-toggle, input[type='checkbox']"
    ).first
    if not checkbox.is_checked():
        checkbox.click()
    assert checkbox.is_checked(), (
        f'Setup failed: card "{card_title}" could not be marked complete'
    )


# ── Given: description ────────────────────────────────────────────────────────

@given(parsers.parse('the card "{card_title}" has the description "{description}"'))
def card_has_description(page, card_title, description):
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
    desc_field = detail.locator(
        "textarea.card-description, textarea.description, textarea, "
        "input.description, [data-field='description']"
    ).first
    desc_field.fill(description)
    save_button = detail.locator(
        "button.save, button.save-description, button[data-action='save'], button:has-text('Save')"
    )
    if save_button.count() > 0:
        save_button.first.click()
    else:
        desc_field.press("Tab")
    close_button = detail.locator(
        "button.close, button[data-action='close'], button:has-text('Close'), button:has-text('×')"
    )
    if close_button.count() > 0:
        close_button.first.click()


# ── When ──────────────────────────────────────────────────────────────────────

@when("I reload the page")
def reload_page(page):
    page.reload()


# ── Then: label ───────────────────────────────────────────────────────────────

@then(parsers.parse('the card "{card_title}" has a "{color}" label'))
def card_has_color_label(page, card_title, color):
    card = page.locator(".card", has_text=card_title).first
    label = card.locator(
        f".label-{color}, [data-color='{color}'], .label[data-color='{color}']"
    )
    assert label.count() > 0, (
        f'Expected card "{card_title}" to have a "{color}" label after reload, but none found'
    )
    assert label.first.is_visible(), (
        f'Expected "{color}" label on card "{card_title}" to be visible after reload'
    )


# ── Then: due date ────────────────────────────────────────────────────────────

@then(parsers.parse('the card "{card_title}" shows the due date "{due_date}"'))
def card_shows_due_date(page, card_title, due_date):
    card = page.locator(".card", has_text=card_title).first
    date_input = card.locator("input[type='date']")
    if date_input.count() > 0:
        actual = date_input.first.input_value()
        assert actual == due_date, (
            f'Expected due date "{due_date}" after reload, got "{actual}"'
        )
        return
    due_date_el = card.locator(
        ".due-date, .card-due-date, [data-field='due-date'], [class*='due']"
    )
    if due_date_el.count() > 0:
        actual = due_date_el.first.inner_text()
        assert due_date in actual, (
            f'Expected due date "{due_date}" visible on card "{card_title}" after reload, '
            f'got "{actual}"'
        )
        return
    card.click()
    detail = page.locator(".card-modal, .card-detail, .modal, [role='dialog']")
    detail.wait_for(state="visible", timeout=5000)
    date_field = detail.locator("input[type='date']").first
    actual = date_field.input_value()
    assert actual == due_date, (
        f'Expected due date "{due_date}" after reload, got "{actual}"'
    )


# ── Then: completion ──────────────────────────────────────────────────────────

@then(parsers.parse('the card "{card_title}" is shown as complete'))
def card_shown_as_complete(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    checkbox = card.locator(
        "input[type='checkbox'].complete-toggle, input[type='checkbox']"
    ).first
    assert checkbox.is_checked(), (
        f'Expected card "{card_title}" checkbox to be checked (complete) after reload'
    )
    card_classes = card.get_attribute("class") or ""
    assert "complete" in card_classes or "done" in card_classes, (
        f'Expected card "{card_title}" to have "complete" or "done" CSS class after reload, '
        f'got: "{card_classes}"'
    )


# ── Then: description ─────────────────────────────────────────────────────────

@then(parsers.parse('the card "{card_title}" shows the description "{description}"'))
def card_shows_description(page, card_title, description):
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
    desc_field = detail.locator(
        "textarea.card-description, textarea.description, textarea, "
        "input.description, [data-field='description']"
    ).first
    tag = desc_field.evaluate("el => el.tagName").lower()
    actual = (
        desc_field.input_value()
        if tag in ("input", "textarea")
        else desc_field.inner_text()
    )
    assert actual == description, (
        f'Expected description "{description}" after reload, got "{actual}"'
    )
