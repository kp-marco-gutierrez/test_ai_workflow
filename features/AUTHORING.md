# Authoring specs

A spec is the contract for the whole AI pipeline. Tests, implementation, and
review are all derived from it, so it must be well-formed and tightly scoped.

## Format rules (enforced by `scripts/validate_spec.py`)

- One `Feature:` per file, with a name.
- At least one `Scenario:` (or `Scenario Outline:`).
- Every scenario has **Given / When / Then**. A `Background:` `Given` counts as
  the Given for every scenario in the file.
- Every step has text. Use concrete, checkable values (exact strings, numbers,
  named states) rather than vague descriptions.

## Sizing rules (enforced by `scripts/validate_spec.py`)

A spec must be small enough to implement and test as **one self-contained
unit**. The guardrail rejects a spec and prints a suggested breakdown when:

| Limit | Default |
|-------|---------|
| Scenarios per feature | 7 |
| Total steps per feature | 30 |
| Steps in a single scenario | 9 |
| Features per file | 1 |

Rule of thumb: if you can't describe the capability in one sentence, split it
into multiple `.feature` files.

## Triggering the pipeline

File the spec as a GitHub Issue (the **BDD Spec** issue template) and, once it's
ready and reviewed, comment **`@go-develop`** on the issue. That one comment
drives the whole pipeline: validate the spec → AI1 writes tests → tests must
fail → AI-Red-Team reviews the tests → AI2 implements until tests pass → ChatGPT
code review (with a fix loop) → approve → full CI → squash-merge.

Run the guardrail locally before filing, if you like:

```bash
python3 scripts/validate_spec.py features/
```
