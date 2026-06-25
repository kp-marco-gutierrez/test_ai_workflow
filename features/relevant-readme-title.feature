Feature: Relevant README title
  As a reader
  I want the README title to name the product clearly
  So that I know what this repo is at a glance

  Background:
    Given the project README

  Scenario: The top heading names the product
    When I read the first heading of the README
    Then it contains "Trello-lite"
    And it is not just "test_ai_workflow"
