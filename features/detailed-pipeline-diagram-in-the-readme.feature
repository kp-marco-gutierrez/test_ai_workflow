Feature: Detailed pipeline diagram in the README
  As a reader
  I want the "How it works" diagram to show every pipeline stage
  So that I understand the full flow, not a simplified version

  Background:
    Given the project README

  Scenario: The diagram shows the early gates
    When I read the "How it works" section
    Then it shows a step for the AI-Red-Team test review
    And it shows a step for the dry-run gate where tests must fail first

  Scenario: The diagram shows implement, verify, review and merge
    When I read the "How it works" section
    Then it shows steps for implement, verify, code review, and squash-merge
