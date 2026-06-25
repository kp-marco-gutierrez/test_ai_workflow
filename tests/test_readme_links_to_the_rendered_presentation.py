import os
import re

from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/readme-links-to-the-rendered-presentation.feature")

_README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")

_SLIDE_DECK_RE = re.compile(r"\[.*?pipeline-deck.*?\]\((.*?)\)", re.IGNORECASE)


@given("the project README", target_fixture="readme")
def the_project_readme():
    with open(_README_PATH) as fh:
        return fh.read()


@when("I read the slide-deck link", target_fixture="slide_deck_url")
def read_the_slide_deck_link(readme):
    match = _SLIDE_DECK_RE.search(readme)
    assert match, "README does not contain a slide-deck link matching pipeline-deck"
    return match.group(1)


@then(parsers.parse('it points to "{expected_url}"'))
def it_points_to(slide_deck_url, expected_url):
    assert slide_deck_url == expected_url, (
        f"Slide-deck link is '{slide_deck_url}', expected '{expected_url}'"
    )


@then(parsers.parse('it is not the bare repository path "{bare_path}"'))
def it_is_not_the_bare_path(slide_deck_url, bare_path):
    assert slide_deck_url != bare_path, (
        f"Slide-deck link is the bare repo path '{bare_path}' — "
        "it should be the full GitHub Pages URL"
    )
