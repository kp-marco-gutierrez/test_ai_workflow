from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/show-the-label-color-on-a-card.feature")


@given(parsers.parse('the card "{card_title}" has a "{color}" label'))
def card_has_label_setup(page, card_title, color):
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
    color_indicator = card.locator(
        f".label-{color}, [data-color='{color}'], .card-label-{color}, "
        f".label-color-{color}, [data-label-color='{color}']"
    )
    assert color_indicator.count() > 0, (
        f'Setup failed: "{color}" label color indicator not found on card "{card_title}" after adding'
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


@then(parsers.parse('the card "{card_title}" shows a "{color}" label color'))
def card_shows_label_color(page, card_title, color):
    card = page.locator(".card", has_text=card_title).first
    color_indicator = card.locator(
        f".label-{color}, [data-color='{color}'], .card-label-{color}, "
        f".label-color-{color}, [data-label-color='{color}']"
    )
    assert color_indicator.count() > 0, (
        f'Expected card "{card_title}" to show a "{color}" label color indicator, '
        f'but no matching element found'
    )
    assert color_indicator.first.is_visible(), (
        f'Expected "{color}" label color indicator on card "{card_title}" to be visible'
    )


@then(parsers.parse('the card "{card_title}" shows no label color'))
def card_shows_no_label_color(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    color_indicators = card.locator(
        ".label-green, .label-red, .label-blue, .label-yellow, .label-purple, .label-orange, "
        ".label-pink, .label-teal, .label-color, .card-label-color, [data-label-color]"
    )
    assert color_indicators.count() == 0, (
        f'Expected card "{card_title}" to show no label color, '
        f'but found {color_indicators.count()} color indicator(s)'
    )
