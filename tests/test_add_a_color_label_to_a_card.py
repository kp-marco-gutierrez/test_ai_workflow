from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/add-a-color-label-to-a-card.feature")


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


@when(parsers.parse('I add a "{color}" label to the card "{card_title}"'))
def add_label_to_card(page, color, card_title):
    card = page.locator(".card", has_text=card_title).first
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
    color_option.first.wait_for(state="visible", timeout=5000)
    color_option.first.click()


@when(parsers.parse('I remove the "{color}" label from the card "{card_title}"'))
def remove_label_from_card(page, color, card_title):
    card = page.locator(".card", has_text=card_title).first
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
    color_option.first.wait_for(state="visible", timeout=5000)
    color_option.first.click()


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


@then(parsers.parse('the card "{card_title}" has no labels'))
def card_has_no_labels(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    labels = card.locator(".label, [data-color], .card-label")
    assert labels.count() == 0, (
        f'Expected card "{card_title}" to have no labels, but found {labels.count()}'
    )
