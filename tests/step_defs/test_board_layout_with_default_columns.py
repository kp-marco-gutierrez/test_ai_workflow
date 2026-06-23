import pytest
from pytest_bdd import scenarios, given, when, then

from app.server import StaticServer
from app.board_page import BoardPage

scenarios('../../features/board-layout-with-default-columns.feature')


@pytest.fixture
def static_server():
    server = StaticServer(root='.')
    server.start()
    yield server
    server.stop()


@given('the board app is open', target_fixture='board_page')
def board_app_is_open(static_server):
    page = BoardPage(base_url=static_server.url)
    page.open()
    return page


@when('the board loads')
def board_loads(board_page):
    board_page.wait_for_load()


@then('the columns "To Do", "Doing", "Done" are visible in that order')
def columns_visible_in_order(board_page):
    assert board_page.get_column_names() == ["To Do", "Doing", "Done"]


@then('each column shows 0 cards')
def each_column_shows_0_cards(board_page):
    for count in board_page.get_card_counts():
        assert count == 0


@then('the page heading is "Trello-lite"')
def page_heading_is_trello_lite(board_page):
    assert board_page.get_heading() == "Trello-lite"
