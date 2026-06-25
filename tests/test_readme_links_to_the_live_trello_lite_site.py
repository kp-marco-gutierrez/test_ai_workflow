import os
import re

from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/readme-links-to-the-live-trello-lite-site.feature")

_README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")

_LIVE_URL = "https://kp-marco-gutierrez.github.io/test_ai_workflow/"


@given("the project README", target_fixture="readme")
def the_project_readme():
    with open(_README_PATH) as fh:
        return fh.read()


@when("I read the README")
def read_the_readme(readme):
    pass


@then(parsers.parse('it links to "{url}"'))
def it_links_to_url(readme, url):
    assert url in readme, f"README does not contain a link to '{url}'"


@then("the link is labelled as the live Trello-lite app")
def link_is_labelled_as_live_app(readme):
    pattern = r'\[([^\]]+)\]\(' + re.escape(_LIVE_URL) + r'\)'
    match = re.search(pattern, readme)
    assert match, (
        f"README does not contain a markdown link to '{_LIVE_URL}'; "
        "expected format: [label](url)"
    )
    label = match.group(1).lower()
    assert any(word in label for word in ("trello", "live", "app")), (
        f"Link label '{match.group(1)}' does not describe the live Trello-lite app"
    )
