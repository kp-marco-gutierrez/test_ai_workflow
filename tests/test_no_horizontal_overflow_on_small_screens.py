import os
from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/no-horizontal-overflow-on-small-screens.feature")


@given(
    parsers.parse("the board app is open on a {width:d}px-wide screen"),
    target_fixture="page",
)
def board_app_open_on_viewport(_browser, width):
    index_html = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "index.html")
    )
    page = _browser.new_page(viewport={"width": width, "height": 667})
    page.goto(f"file://{index_html}")
    return page


@when("the board loads")
def board_loads(page):
    page.wait_for_load_state("domcontentloaded")


@then("the page has no horizontal scrolling")
def no_horizontal_scrolling(page):
    scroll_width = page.evaluate(
        "Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)"
    )
    inner_width = page.evaluate("window.innerWidth")
    assert scroll_width <= inner_width, (
        f"Page overflows horizontally: scrollWidth={scroll_width}px > "
        f"innerWidth={inner_width}px (viewport width)"
    )
