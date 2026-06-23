---
name: BDD Spec
about: Describe one capability as a BDD spec. AI generates the tests from it.
title: "[spec]: <one-line capability>"
labels: ["spec"]
---

<!--
Fill in the Gherkin spec below, replacing the <placeholders>.

RULES (enforced by the guardrail — see features/AUTHORING.md):
  - One Feature, a handful of scenarios. If it's big, split it into more issues.
  - Every Scenario needs Given / When / Then (a Background Given counts).
  - Use concrete, checkable values (exact strings, numbers, named states).

TO TRIGGER TEST GENERATION:
  Once the spec is ready and reviewed, add a comment on this issue containing
  `@generate-tests`. That runs the guardrail and, if it passes, opens a PR with
  the generated pytest-bdd tests.
-->

```gherkin
Feature: <capability name>
  As a <role>
  I want <goal>
  So that <benefit>

  Background:
    Given <shared precondition>

  Scenario: <happy path name>
    Given <precondition>
    When <action>
    Then <expected outcome>

  Scenario: <error or edge case name>
    Given <precondition>
    When <action>
    Then <expected outcome>
```
