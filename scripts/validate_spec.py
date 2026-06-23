#!/usr/bin/env python3
"""Step-1 spec guardrail for the AI-only pipeline.

Two deterministic checks, no external dependencies:

  1. BDD FORMAT  — the .feature file is well-formed Gherkin: a Feature with at
                   least one Scenario, and every Scenario has Given / When /
                   Then (a Background `Given` satisfies the Given for every
                   scenario in the file). Steps must have text.

  2. TASK SIZE   — the spec is small enough to implement and test as ONE
                   self-contained unit. If it's too big, the spec is rejected
                   and a suggested breakdown into smaller specs is printed.

Usage:
    python scripts/validate_spec.py features/login.feature [more.feature ...]
    python scripts/validate_spec.py features/              # all *.feature
    python scripts/validate_spec.py --list-tagged features/  # print tagged paths

Exit code is non-zero if any spec fails a check (so CI gates on it).
"""

import os
import re
import sys

# --- Task-size thresholds (tune to taste) -----------------------------------
MAX_SCENARIOS_PER_FEATURE = 7   # more than this => likely several tasks
MAX_STEPS_PER_FEATURE = 30      # total steps across background + scenarios
MAX_STEPS_PER_SCENARIO = 9      # one scenario doing too much

TRIGGER_TAG = "@generate-tests"

PRIMARY = ("given", "when", "then")
STEP_KEYWORDS = PRIMARY + ("and", "but", "*")


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "scenario"


def parse(path):
    """Very small Gherkin reader. Returns (features, parse_errors)."""
    features = []
    errors = []
    pending_tags = []
    feature = None
    block = None          # current scenario or background dict
    in_examples = False
    examples_header_seen = False

    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()

    for n, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("@"):
            pending_tags.extend(line.split())
            continue

        if line.startswith("Feature:"):
            feature = {
                "name": line[len("Feature:"):].strip(),
                "line": n,
                "tags": pending_tags,
                "background": None,
                "scenarios": [],
            }
            features.append(feature)
            pending_tags = []
            block = None
            in_examples = False
            continue

        if feature is None:
            errors.append(f"{path}:{n}: content before any 'Feature:' line")
            continue

        if line.startswith("Background:"):
            block = {"kind": "background", "name": "Background", "line": n, "steps": []}
            feature["background"] = block
            in_examples = False
            continue

        if line.startswith("Scenario Outline:") or line.startswith("Scenario:"):
            label = "Scenario Outline:" if line.startswith("Scenario Outline:") else "Scenario:"
            block = {
                "kind": "scenario",
                "name": line[len(label):].strip(),
                "line": n,
                "tags": pending_tags,
                "steps": [],
                "example_rows": 0,
            }
            feature["scenarios"].append(block)
            pending_tags = []
            in_examples = False
            continue

        if line.startswith("Examples:"):
            in_examples = True
            examples_header_seen = False
            continue

        if line.startswith("|"):
            if in_examples and block and block["kind"] == "scenario":
                if examples_header_seen:
                    block["example_rows"] += 1
                else:
                    examples_header_seen = True
            continue

        first = line.split(None, 1)
        keyword = first[0].lower()
        if keyword in STEP_KEYWORDS:
            text = first[1].strip() if len(first) > 1 else ""
            if block is None:
                errors.append(f"{path}:{n}: step '{line}' outside any Scenario/Background")
            else:
                block["steps"].append({"kw": keyword, "text": text, "line": n})
            continue

        # Non-keyword line: allowed only as free-text Feature description
        # (before the first Scenario/Background). Otherwise it's junk.
        if block is not None:
            errors.append(f"{path}:{n}: unrecognized line '{line}'")

    return features, errors


def check_format(path, features):
    errors = []
    if not features:
        return [f"{path}: no 'Feature:' found"]

    for feat in features:
        if not feat["name"]:
            errors.append(f"{path}:{feat['line']}: Feature has no name")
        bg = feat["background"]
        bg_has_given = bool(bg and any(s["kw"] == "given" for s in bg["steps"]))

        if not feat["scenarios"]:
            errors.append(f"{path}:{feat['line']}: Feature '{feat['name']}' has no scenarios")

        for sc in feat["scenarios"]:
            if not sc["name"]:
                errors.append(f"{path}:{sc['line']}: Scenario has no name")
            for s in sc["steps"]:
                if not s["text"]:
                    errors.append(f"{path}:{s['line']}: step '{s['kw']}' has no text")

            kinds = {s["kw"] for s in sc["steps"]}
            has_given = "given" in kinds or bg_has_given
            has_when = "when" in kinds
            has_then = "then" in kinds
            missing = []
            if not has_given:
                missing.append("Given")
            if not has_when:
                missing.append("When")
            if not has_then:
                missing.append("Then")
            if missing:
                errors.append(
                    f"{path}:{sc['line']}: Scenario '{sc['name']}' is missing "
                    f"{', '.join(missing)} (a Background Given counts as Given)"
                )
    return errors


def check_size(path, features):
    """Return (too_big, suggestion_lines)."""
    problems = []

    if len(features) > 1:
        problems.append(
            f"file defines {len(features)} Features — keep one Feature per spec file"
        )

    for feat in features:
        n_sc = len(feat["scenarios"])
        bg_steps = len(feat["background"]["steps"]) if feat["background"] else 0
        total_steps = bg_steps + sum(len(sc["steps"]) for sc in feat["scenarios"])

        if n_sc > MAX_SCENARIOS_PER_FEATURE:
            problems.append(
                f"Feature '{feat['name']}' has {n_sc} scenarios "
                f"(max {MAX_SCENARIOS_PER_FEATURE})"
            )
        if total_steps > MAX_STEPS_PER_FEATURE:
            problems.append(
                f"Feature '{feat['name']}' has {total_steps} steps "
                f"(max {MAX_STEPS_PER_FEATURE})"
            )
        for sc in feat["scenarios"]:
            if len(sc["steps"]) > MAX_STEPS_PER_SCENARIO:
                problems.append(
                    f"Scenario '{sc['name']}' has {len(sc['steps'])} steps "
                    f"(max {MAX_STEPS_PER_SCENARIO}) — it likely tests more than "
                    f"one behavior"
                )

    if not problems:
        return False, []

    # Build a concrete breakdown suggestion.
    suggestion = ["", "Suggested breakdown:"]
    if len(features) > 1:
        for feat in features:
            suggestion.append(f"  - features/{slug(feat['name'])}.feature  ({feat['name']})")
        return True, problems, suggestion

    feat = features[0]
    scs = feat["scenarios"]
    if len(scs) > MAX_SCENARIOS_PER_FEATURE:
        # chunk scenarios into smaller specs
        chunk = MAX_SCENARIOS_PER_FEATURE
        for i in range(0, len(scs), chunk):
            group = scs[i:i + chunk]
            fname = f"features/{slug(feat['name'])}-{i // chunk + 1}.feature"
            names = "; ".join(sc["name"] for sc in group)
            suggestion.append(f"  - {fname}: {names}")
    else:
        suggestion.append(
            "  - Split the oversized scenario(s) into one scenario per distinct "
            "behavior, each asserting a single outcome."
        )
    suggestion.append("")
    suggestion.append(
        "A right-sized spec is one capability you could implement and test in "
        "isolation. If you can't describe it in one sentence, split it."
    )
    return True, problems, suggestion


def expand(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in sorted(files):
                    if f.endswith(".feature"):
                        out.append(os.path.join(root, f))
        else:
            out.append(p)
    return out


def main(argv):
    list_tagged = False
    args = []
    for a in argv:
        if a == "--list-tagged":
            list_tagged = True
        else:
            args.append(a)

    if not args:
        print("usage: validate_spec.py [--list-tagged] <path...>", file=sys.stderr)
        return 2

    files = expand(args)

    if list_tagged:
        for path in files:
            features, _ = parse(path)
            if any(TRIGGER_TAG in feat["tags"] for feat in features):
                print(path)
        return 0

    failed = False
    for path in files:
        features, parse_errors = parse(path)
        fmt_errors = parse_errors + check_format(path, features)
        size_result = check_size(path, features)
        too_big = size_result[0]

        if not fmt_errors and not too_big:
            tagged = any(TRIGGER_TAG in feat["tags"] for feat in features)
            mark = " [@generate-tests]" if tagged else ""
            print(f"OK    {path}{mark}")
            continue

        failed = True
        if fmt_errors:
            print(f"FAIL  {path}  — invalid BDD format")
            for e in fmt_errors:
                print(f"        {e}")
        if too_big:
            problems, suggestion = size_result[1], size_result[2]
            print(f"FAIL  {path}  — task too large to be self-contained")
            for p in problems:
                print(f"        {p}")
            for line in suggestion:
                print(f"      {line}" if line else "")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
