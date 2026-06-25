import os

from playwright.sync_api import sync_playwright
from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/header-controls-fit-small-screens.feature")


@given(parsers.parse("the board app is open on a {width:d}px-wide screen"), target_fixture="page")
def board_app_open_on_narrow_screen(width):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch()
    page = browser.new_page(viewport={"width": width, "height": 812})
    index_html = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "index.html")
    )
    page.goto(f"file://{index_html}")
    page.wait_for_load_state("domcontentloaded")
    # Store playwright/browser refs on the page object so they can be closed
    page._playwright_ref = playwright
    page._browser_ref = browser
    return page


@when("the board loads")
def board_loads(page):
    page.wait_for_load_state("domcontentloaded")
    # Wait for a recognisable board element so we know the app has rendered
    page.locator("header, .header, #header, .board-header, .app-header").first.wait_for(
        state="attached", timeout=5000
    )


@then("the header content fits within the screen width")
def header_content_fits_screen_width(page):
    viewport_width = page.viewport_size["width"]

    # Check that the page has no horizontal scroll overflow caused by the header
    scroll_overflow = page.evaluate(
        """() => {
            const header = document.querySelector(
                'header, .header, #header, .board-header, .app-header'
            );
            if (!header) return { error: 'header element not found' };
            const rect = header.getBoundingClientRect();
            return {
                headerRight: rect.right,
                headerLeft: rect.left,
                headerWidth: rect.width,
                viewportWidth: window.innerWidth,
                overflows: rect.right > window.innerWidth || rect.left < 0,
            };
        }"""
    )

    assert "error" not in scroll_overflow, (
        f"Could not find header element: {scroll_overflow['error']}"
    )
    assert not scroll_overflow["overflows"], (
        f"Header content overflows the {viewport_width}px-wide screen: "
        f"header spans {scroll_overflow['headerLeft']:.1f}px to "
        f"{scroll_overflow['headerRight']:.1f}px "
        f"(viewport is {scroll_overflow['viewportWidth']}px wide)"
    )
