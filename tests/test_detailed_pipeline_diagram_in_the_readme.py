import os
import re

from pytest_bdd import given, when, then, scenarios

scenarios("../features/detailed-pipeline-diagram-in-the-readme.feature")

_README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")

_HOW_IT_WORKS_SECTION = None


@given("the project README", target_fixture="readme")
def the_project_readme():
    with open(_README_PATH) as fh:
        return fh.read()


@when('I read the "How it works" section', target_fixture="how_it_works")
def read_how_it_works_section(readme):
    # Extract content from the "How it works" heading to the next same-level heading
    match = re.search(
        r"#+\s*How it works\b(.*?)(?=\n#+\s|\Z)",
        readme,
        re.DOTALL | re.IGNORECASE,
    )
    assert match, 'README does not contain a "How it works" section'
    return match.group(1)


@then("it shows a step for the AI-Red-Team test review")
def shows_ai_red_team_step(how_it_works):
    assert "AI-Red-Team" in how_it_works, (
        '"How it works" section does not show a step for the AI-Red-Team test review'
    )


@then("it shows a step for the dry-run gate where tests must fail first")
def shows_dry_run_gate_step(how_it_works):
    lower = how_it_works.lower()
    assert "dry-run" in lower or "dry run" in lower, (
        '"How it works" section does not show a step for the dry-run gate'
    )
    assert "fail" in lower, (
        '"How it works" section does not indicate that tests must fail first'
    )


@then("it shows steps for implement, verify, code review, and squash-merge")
def shows_implement_verify_review_merge_steps(how_it_works):
    lower = how_it_works.lower()
    for keyword in ("implement", "verify", "code review", "squash-merge"):
        assert keyword in lower, (
            f'"How it works" section does not show a step for "{keyword}"'
        )
