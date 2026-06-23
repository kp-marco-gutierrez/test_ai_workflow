# =============================================================================
# BDD SPEC TEMPLATE  (Step 1 of the AI-only pipeline)
# -----------------------------------------------------------------------------
# This file is the *contract*. Everything downstream (tests, code, review) is
# derived from it, so it must be well-formed and tightly scoped.
#
# HOW GENERATION IS TRIGGERED
#   Add the `@generate-tests` tag (below) and push. The "Generate BDD Tests"
#   workflow runs the spec guardrail, then has AI1 generate pytest-bdd step
#   definitions from this spec.
#
# THE GUARDRAIL (scripts/validate_spec.py) CHECKS TWO THINGS
#   1. BDD format  — a Feature with at least one Scenario, and every Scenario
#                    has Given / When / Then (a Background Given counts).
#   2. Task size   — the spec is small enough to build and test as ONE
#                    self-contained unit. If it's too big, the guardrail fails
#                    and prints a suggested breakdown into smaller specs.
#                    Keep it to a single Feature, a handful of scenarios.
#
# Replace the example below with your real spec; keep the @generate-tests tag.
# =============================================================================

@generate-tests
Feature: User login
  As a registered user
  I want to authenticate with my email and password
  So that I can access my account dashboard

  Background:
    Given a registered user with email "ada@example.com" and password "Pa55word!"

  Scenario: Successful login with valid credentials
    Given the user is on the login page
    When the user submits email "ada@example.com" and password "Pa55word!"
    Then the user is redirected to "/dashboard"
    And the response status code is 200

  Scenario: Rejected login with a wrong password
    Given the user is on the login page
    When the user submits email "ada@example.com" and password "wrong-password"
    Then an error "Invalid credentials" is shown
    And the response status code is 401
