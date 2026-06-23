#!/usr/bin/env python3
"""AI reviewer (ChatGPT) for the AI-only pipeline.

Two modes:

  --mode tests  (default, step 3 — AI-Red-Team)
      Critique the generated BDD tests against their .feature specs: coverage,
      faithful assertions, auto-pass smells, spec drift.

  --mode code   (step 8 — code review)
      Review the implementation that was written to satisfy the spec, with a
      senior code-reviewer hat: correctness vs spec, DRY, architecture,
      security, readability/maintainability.

Writes the review to review.md and prints the verdict (APPROVE or
REQUEST_CHANGES) to stdout so the workflow can branch on it.

Env:
  OPENAI_API_KEY  (required)
  OPENAI_MODEL    (default: gpt-4o)
"""

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
CODE_EXTS = (".py", ".js", ".ts", ".html", ".css")
PRUNE_DIRS = {"tests", "features", "scripts", "node_modules", ".git", ".github"}

SYSTEM = {
    "tests": (
        "You are AI-Red-Team, a meticulous adversarial test reviewer in an "
        "automated BDD pipeline. You review generated tests against their "
        "Gherkin specs. You do NOT review or write implementation code."
    ),
    "code": (
        "You are a senior code reviewer in an automated BDD pipeline. You review "
        "the implementation that was written to satisfy a Gherkin spec and its "
        "tests."
    ),
}

INSTRUCTIONS = {
    "tests": """\
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
""",
    "code": """\
Review the implementation against the spec and tests, as a senior reviewer. Be
concrete and actionable — cite file and the relevant code for every point.

1. Correctness — the code actually satisfies the spec's behavior (not just the
   literal tests). Flag gaps or behavior the spec requires but code misses.
2. DRY / simplicity — duplication, dead code, needless complexity.
3. Architecture — sensible structure, separation, naming; for a static GitHub
   Pages app: pure client-side, no backend, relative asset paths.
4. Security — injection/XSS, unsafe DOM, secrets, unsafe defaults.
5. Readability / maintainability.

End your response with a final line that is EXACTLY one of:
VERDICT: APPROVE
VERDICT: REQUEST_CHANGES
""",
}


def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def collect_glob(globs):
    import glob

    out = {}
    for g in globs:
        for p in glob.glob(g, recursive=True):
            if os.path.isfile(p):
                out[p] = read(p)
    return out


def collect_code():
    out = {}
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in PRUNE_DIRS]
        for f in files:
            if f.endswith(CODE_EXTS):
                p = os.path.join(root, f)
                out[p] = read(p)
    return out


def block(files):
    if not files:
        return "(none found)"
    return "\n\n".join(
        f"### {path}\n```\n{content}\n```" for path, content in sorted(files.items())
    )


def call_openai(system, user):
    payload = json.dumps(
        {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system},
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
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"].strip()


def main(argv):
    mode = "tests"
    if "--mode" in argv:
        mode = argv[argv.index("--mode") + 1]
    if mode not in ("tests", "code"):
        print(f"unknown mode: {mode}", file=sys.stderr)
        return 2
    if not API_KEY:
        print("OPENAI_API_KEY is not set", file=sys.stderr)
        return 2

    specs = collect_glob(SPEC_GLOBS)
    if mode == "tests":
        subject = collect_glob(TEST_GLOBS)
        subject_label = "Generated tests"
        empty_msg = "No test files found to review."
    else:
        subject = collect_code()
        subject_label = "Implementation"
        empty_msg = "No implementation files found to review."

    title = "🔴 AI-Red-Team review (ChatGPT)" if mode == "tests" else "🧐 Code review (ChatGPT)"

    if not subject:
        with open("review.md", "w", encoding="utf-8") as fh:
            fh.write(f"## {title}\n\n_{empty_msg}_\n")
        # No tests to review -> nothing to block on; no code -> needs changes.
        print("APPROVE" if mode == "tests" else "REQUEST_CHANGES")
        return 0

    user = (
        f"## BDD spec(s)\n{block(specs)}\n\n"
        f"## {subject_label}\n{block(subject)}\n\n"
        f"## Task\n{INSTRUCTIONS[mode]}"
    )

    try:
        review = call_openai(SYSTEM[mode], user)
    except urllib.error.HTTPError as e:
        print(f"OpenAI API error {e.code}: {e.read().decode()}", file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"OpenAI request failed: {e}", file=sys.stderr)
        return 1

    with open("review.md", "w", encoding="utf-8") as fh:
        fh.write(f"## {title}\n\n{review}\n")

    up = review.upper()
    if "VERDICT: APPROVE" in up and "VERDICT: REQUEST_CHANGES" not in up:
        print("APPROVE")
    else:
        print("REQUEST_CHANGES")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
