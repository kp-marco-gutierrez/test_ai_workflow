import os
import re

from pytest_bdd import given, when, then, scenarios, parsers

scenarios("../features/readme-documents-the-delivery-pipeline.feature")

_README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")


@given("the repository README", target_fixture="readme")
def the_repository_readme():
    with open(_README_PATH) as fh:
        return fh.read()


@when("I read the README")
def read_the_readme(readme):
    pass


@then(parsers.parse('it contains a link to "{path}"'))
def it_contains_a_link(readme, path):
    assert path in readme, f"README does not contain a link to '{path}'"


@then(parsers.parse('it contains a fenced "{lang}" diagram block'))
def it_contains_fenced_block(readme, lang):
    assert f"```{lang}" in readme, (
        f"README does not contain a fenced '{lang}' block"
    )


@then(
    parsers.re(
        r'the diagram references "(?P<a>[^"]+)", "(?P<b>[^"]+)", "(?P<c>[^"]+)", and "(?P<d>[^"]+)"'
    )
)
def diagram_references_keywords(readme, a, b, c, d):
    match = re.search(r"```mermaid(.*?)```", readme, re.DOTALL)
    assert match, "README does not contain a mermaid diagram block"
    diagram = match.group(1)
    for word in (a, b, c, d):
        assert word in diagram, f"Mermaid diagram does not reference '{word}'"


@then("it explains that AI generates code and deterministic CI decides pass or fail")
def it_explains_core_principle(readme):
    lower = readme.lower()
    assert "deterministic" in lower, "README does not contain 'deterministic'"
    assert "pass or fail" in lower, "README does not contain 'pass or fail'"
