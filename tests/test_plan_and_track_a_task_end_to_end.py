from pytest_bdd import when, scenarios

scenarios("../features/plan-and-track-a-task-end-to-end.feature")


@when("I reload the page")
def reload_the_page(page):
    page.reload()
    page.wait_for_load_state("load")
