import os
import re

from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/relevant-readme-title.feature")

_README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")


@given("the project README", target_fixture="readme")
def the_project_readme():
    with open(_README_PATH) as fh:
        return fh.read()


@when("I read the first heading of the README", target_fixture="first_heading")
def read_first_heading(readme):
    match = re.search(r"^#\s+(.+)$", readme, re.MULTILINE)
    assert match, "README has no top-level heading"
    return match.group(1).strip()


@then(parsers.parse('it contains "{text}"'))
def it_contains_text(first_heading, text):
    assert text in first_heading, (
        f"README first heading {first_heading!r} does not contain {text!r}"
    )


@then(parsers.parse('it is not just "{text}"'))
def it_is_not_just(first_heading, text):
    assert first_heading != text, (
        f"README first heading is still the placeholder {text!r}"
    )
