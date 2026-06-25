Feature: Reorder lists
  As a user
  I want to move a list left or right
  So that I can arrange my board

  Background:
    Given the board app is open

  Scenario: Move a list left
    When I move the "Doing" list left
    Then the board lists "Doing" before "To Do"

  Scenario: Move a list right
    When I move the "To Do" list right
    Then the board lists "Doing" before "To Do"
