import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from app.board import Board  # AI2 implements this

scenarios("../../features/board-layout-with-default-columns.feature")


@pytest.fixture
def board():
    return Board()


@given("the board app is open", target_fixture="ctx")
def board_app_is_open(board):
    return {"board": board}


@when("the board loads")
def board_loads(ctx):
    ctx["board"].load()


@then(parsers.parse('the columns "{c1}", "{c2}", "{c3}" are visible in that order'))
def columns_visible_in_order(ctx, c1, c2, c3):
    columns = ctx["board"].get_columns()
    assert [col.name for col in columns] == [c1, c2, c3]


@then("each column shows 0 cards")
def each_column_shows_0_cards(ctx):
    for col in ctx["board"].get_columns():
        assert col.card_count == 0


@then(parsers.parse('the page heading is "{heading}"'))
def page_heading_is(ctx, heading):
    assert ctx["board"].get_heading() == heading
