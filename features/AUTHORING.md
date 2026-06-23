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

## Triggering generation

Add the `@generate-tests` tag above the `Feature:` and push. The
**Generate BDD Tests** workflow runs the guardrail, then has AI1 generate
pytest-bdd step definitions under `tests/step_defs/`.

```gherkin
@generate-tests
Feature: ...
```

Run the guardrail locally before pushing:

```bash
python3 scripts/validate_spec.py features/
```
