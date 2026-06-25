Feature: Clear completed cards from a list
  As a user
  I want to remove all completed cards from a list
  So that I can tidy up finished work

  Background:
    Given the board app is open
    And a completed card "Done task" is in the "Doing" column
    And a card "Open task" is in the "Doing" column

  Scenario: Clearing removes only completed cards
    When I clear completed cards from the "Doing" column
    Then the card "Done task" is hidden
    And the card "Open task" is visible

  Scenario: Open cards remain after clearing
    When I clear completed cards from the "Doing" column
    Then the "Doing" column shows 1 card
