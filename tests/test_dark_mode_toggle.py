from pytest_bdd import given, when, then, scenarios

scenarios("../features/dark-mode-toggle.feature")


def _click_theme_toggle(page):
    toggle = page.locator(
        ".theme-toggle, #theme-toggle, button.theme-toggle, "
        "[data-action='toggle-theme'], button[aria-label*='theme' i], "
        "button[title*='theme' i], button[aria-label*='dark' i], "
        "button[title*='dark' i]"
    ).first
    toggle.click()


@given("I click the theme toggle")
def given_click_theme_toggle(page):
    _click_theme_toggle(page)


@when("I click the theme toggle")
def when_click_theme_toggle(page):
    _click_theme_toggle(page)


@when("I reload the page")
def reload_page(page):
    page.reload()
    page.wait_for_load_state("domcontentloaded")


@then("the page is in dark mode")
def page_is_in_dark_mode(page):
    dark_on_html = page.evaluate(
        'document.documentElement.getAttribute("data-theme")'
    )
    dark_on_body = page.evaluate(
        'document.body.getAttribute("data-theme")'
    )
    assert dark_on_html == "dark" or dark_on_body == "dark", (
        f'Expected data-theme="dark" on <html> or <body>, '
        f"got html={dark_on_html!r} body={dark_on_body!r}"
    )
