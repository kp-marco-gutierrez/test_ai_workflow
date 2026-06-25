from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/filter-cards-by-label.feature")


@given(parsers.parse('a card "{card_title}" with a "{color}" label is in the "{column_name}" column'))
def card_with_label_in_column(page, card_title, color, column_name):
    column = page.locator(
        ".column",
        has=page.locator(".column-header", has_text=column_name),
    )
    card_input = column.locator("input.card-input, input[type='text']").first
    card_input.fill(card_title)
    add_button = column.locator("button.add-card, button[type='submit'], .add-card-btn").first
    add_button.click()
    card = column.locator(".card", has_text=card_title)
    assert card.count() > 0, (
        f'Setup failed: card "{card_title}" not found in "{column_name}" column after adding'
    )
    card_el = page.locator(".card", has_text=card_title).first
    label_btn = card_el.locator(
        f"button.label-{color}, button[data-label='{color}'], "
        f".label-{color}, [data-color='{color}'], button:has-text('{color}')"
    )
    if label_btn.count() > 0:
        label_btn.first.click()
    else:
        open_btn = card_el.locator(
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
    label_indicator = card_el.locator(
        f".label-{color}, [data-color='{color}'], .label[data-color='{color}']"
    )
    assert label_indicator.count() > 0, (
        f'Setup failed: "{color}" label not found on card "{card_title}" after adding'
    )


@given(parsers.parse('I filter by the "{color}" label'))
@when(parsers.parse('I filter by the "{color}" label'))
def filter_by_label(page, color):
    label_filter = page.locator(
        f"button.filter-label-{color}, button[data-filter-label='{color}'], "
        f".label-filter [data-color='{color}'], "
        f"[data-filter='{color}'], "
        f".filter-controls button:has-text('{color}'), "
        f"#label-filter-{color}, "
        f"input[type='checkbox'][value='{color}']"
    ).first
    label_filter.click()


@when("I clear the label filter")
def clear_label_filter(page):
    clear_btn = page.locator(
        "button.clear-label-filter, button.clear-filter, "
        "button[data-action='clear-label-filter'], "
        ".filter-controls button:has-text('Clear'), "
        ".filter-controls button:has-text('All'), "
        "button:has-text('Show all')"
    ).first
    clear_btn.click()


@then(parsers.parse('the card "{card_title}" is visible'))
def card_is_visible(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    assert card.is_visible(), f'Expected card "{card_title}" to be visible but it was not'


@then(parsers.parse('the card "{card_title}" is hidden'))
def card_is_hidden(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    assert not card.is_visible(), f'Expected card "{card_title}" to be hidden but it was visible'
