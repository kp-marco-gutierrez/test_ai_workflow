import os

from pytest_bdd import given, when, then, scenarios

scenarios("../features/stack-columns-on-small-screens.feature")


@given("the board app is open on a 375px-wide screen", target_fixture="page")
def board_app_open_narrow(_browser):
    index_html = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "index.html")
    )
    page = _browser.new_page(viewport={"width": 375, "height": 812})
    page.goto(f"file://{index_html}")
    return page


@when("the board loads")
def board_loads(page):
    page.wait_for_load_state("domcontentloaded")


@then('the "Doing" column appears below the "To Do" column')
def doing_appears_below_todo(page):
    todo = page.locator(".column", has=page.locator(".column-header", has_text="To Do"))
    doing = page.locator(".column", has=page.locator(".column-header", has_text="Doing"))

    todo_box = todo.first.bounding_box()
    doing_box = doing.first.bounding_box()

    assert todo_box is not None, '"To Do" column not found in the DOM'
    assert doing_box is not None, '"Doing" column not found in the DOM'

    assert doing_box["y"] >= todo_box["y"] + todo_box["height"], (
        f'"Doing" column top ({doing_box["y"]}px) is not below the bottom of '
        f'"To Do" column ({todo_box["y"] + todo_box["height"]}px). '
        "Columns are not stacked vertically on a 375px-wide screen."
    )


@then('the "To Do" column is at least 90 percent of the screen width')
def todo_fills_screen_width(page):
    viewport = page.viewport_size
    assert viewport is not None, "Cannot determine viewport size"

    todo = page.locator(".column", has=page.locator(".column-header", has_text="To Do"))
    todo_box = todo.first.bounding_box()

    assert todo_box is not None, '"To Do" column not found in the DOM'

    min_width = viewport["width"] * 0.9
    assert todo_box["width"] >= min_width, (
        f'"To Do" column width ({todo_box["width"]}px) is less than 90% of '
        f'the {viewport["width"]}px screen width (need >= {min_width}px). '
        "Add responsive CSS so columns expand to fill the narrow viewport."
    )
