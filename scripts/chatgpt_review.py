#!/usr/bin/env python3
"""AI-Red-Team test review (step 3 of the AI-only pipeline).

Uses the OpenAI API (ChatGPT) to critique the generated BDD tests against their
.feature specs:
  - coverage: every Scenario / Given-When-Then has a real, exercised test
  - faithfulness: assertions match the exact Then outcomes
  - no auto-pass: no truthy-constant asserts, missing assertions, skip/xfail, etc.
  - no spec drift: tests don't invent behavior the spec doesn't state

Writes the review to review.md and prints the verdict (APPROVE or
REQUEST_CHANGES) to stdout so the workflow can branch on it.

Env:
  OPENAI_API_KEY  (required)
  OPENAI_MODEL    (default: gpt-4o)
"""

import glob
import json
import os
import sys
import urllib.error
import urllib.request

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
API_KEY = os.environ.get("OPENAI_API_KEY")

SPEC_GLOBS = ["features/**/*.feature"]
TEST_GLOBS = [
    "tests/**/*.py",
    "tests/**/*.js",
    "tests/**/*.ts",
    "features/step_definitions/**/*.js",
    "features/step_definitions/**/*.ts",
]

SYSTEM = (
    "You are AI-Red-Team, a meticulous adversarial test reviewer in an automated "
    "BDD pipeline. You review generated tests against their Gherkin specs. You do "
    "NOT review or write implementation code."
)

INSTRUCTIONS = """\
Review the generated tests against the BDD spec(s). Be concrete and actionable —
cite the file and the scenario for every point.

1. Coverage — every Scenario, and every Given/When/Then step, in the spec has a
   matching, exercised test. List anything uncovered.
2. Faithfulness — assertions reflect the EXACT Then outcomes (exact strings,
   status codes, counts, order). Flag loose, weak, or wrong assertions.
3. No auto-pass — flag anything that lets a test pass without truly testing:
   asserting constants/truthy, missing assertions, broad try/except,
   skip/xfail, placeholder TODOs, tests that don't call the intended code.
4. No spec drift — tests must not assert behavior the spec doesn't state.

End your response with a final line that is EXACTLY one of:
VERDICT: APPROVE
VERDICT: REQUEST_CHANGES
"""


def collect(globs):
    out = {}
    for g in globs:
        for p in glob.glob(g, recursive=True):
            if os.path.isfile(p):
                with open(p, encoding="utf-8") as fh:
                    out[p] = fh.read()
    return out


def block(files):
    if not files:
        return "(none found)"
    return "\n\n".join(
        f"### {path}\n```\n{content}\n```" for path, content in sorted(files.items())
    )


def main():
    if not API_KEY:
        print("OPENAI_API_KEY is not set", file=sys.stderr)
        return 2

    specs = collect(SPEC_GLOBS)
    tests = collect(TEST_GLOBS)

    if not tests:
        with open("review.md", "w", encoding="utf-8") as fh:
            fh.write("## 🔴 AI-Red-Team review (ChatGPT)\n\n_No test files found to review._\n")
        print("APPROVE")
        return 0

    user = (
        f"## BDD spec(s)\n{block(specs)}\n\n"
        f"## Generated tests\n{block(tests)}\n\n"
        f"## Task\n{INSTRUCTIONS}"
    )

    payload = json.dumps(
        {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user},
            ],
        }
    ).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        print(f"OpenAI API error {e.code}: {e.read().decode()}", file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"OpenAI request failed: {e}", file=sys.stderr)
        return 1

    review = data["choices"][0]["message"]["content"].strip()
    with open("review.md", "w", encoding="utf-8") as fh:
        fh.write("## 🔴 AI-Red-Team review (ChatGPT)\n\n")
        fh.write(review + "\n")

    up = review.upper()
    if "VERDICT: APPROVE" in up and "VERDICT: REQUEST_CHANGES" not in up:
        print("APPROVE")
    else:
        # Default to REQUEST_CHANGES when unclear — fail safe toward scrutiny.
        print("REQUEST_CHANGES")
    return 0


if __name__ == "__main__":
    sys.exit(main())
