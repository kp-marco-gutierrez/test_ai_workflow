from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/filter-cards-by-a-search-term.feature")


@given(parsers.parse('I search for "{term}"'))
@when(parsers.parse('I search for "{term}"'))
def search_for(page, term):
    search_input = page.locator("input#search, input.search-input, input[type='search'], input[placeholder*='earch']").first
    search_input.fill(term)
    search_input.dispatch_event("input")


@when("I clear the search")
def clear_search(page):
    search_input = page.locator("input#search, input.search-input, input[type='search'], input[placeholder*='earch']").first
    search_input.fill("")
    search_input.dispatch_event("input")


@then(parsers.parse('the card "{card_title}" is visible'))
def card_is_visible(page, card_title):
    card = page.locator(".card", has_text=card_title).first
    assert card.is_visible(), f'Expected card "{card_title}" to be visible but it was not'


@then(parsers.parse('the card "{card_title}" is hidden'))
def card_is_hidden(page, card_title):
    cards = page.locator(".card", has_text=card_title)
    assert cards.count() > 0, (
        f'Expected card "{card_title}" to exist in the DOM (hidden by filter), '
        f'but it was not found at all — check that the Background card setup ran'
    )
    assert not cards.first.is_visible(), (
        f'Expected card "{card_title}" to be hidden by the search filter but it was visible'
    )
