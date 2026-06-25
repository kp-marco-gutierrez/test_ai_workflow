import os
import re

from pytest_bdd import given, when, then, scenarios

scenarios("../features/readme-documents-the-app-not-only-the-pipeline.feature")

_README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")


@given("the project README", target_fixture="readme")
def the_project_readme():
    with open(_README_PATH) as fh:
        return fh.read()


@when("I read the README")
def read_the_readme(readme):
    pass


@then("it has a section describing the Trello-lite board app")
def it_has_app_section(readme):
    # Look for a markdown heading that describes the Trello-lite app itself
    headings = re.findall(r"^#{1,4}\s+(.+)$", readme, re.MULTILINE)
    keywords = ("trello", "app", "board", "tool", "about")
    matching = [h for h in headings if any(kw in h.lower() for kw in keywords)]
    assert matching, (
        "README has no section heading describing the Trello-lite app "
        f"(checked {len(headings)} heading(s): {headings})"
    )


@then("that section mentions lists, cards, labels and due dates")
def that_section_mentions_core_concepts(readme):
    lower = readme.lower()
    for term in ("list", "card", "label", "due date"):
        assert term in lower, (
            f"README does not mention '{term}' — expected it in the app description section"
        )


@then("it still has a section describing the delivery pipeline")
def it_still_has_pipeline_section(readme):
    lower = readme.lower()
    assert "pipeline" in lower, (
        "README no longer contains the word 'pipeline' — the pipeline documentation section appears to have been removed"
    )
