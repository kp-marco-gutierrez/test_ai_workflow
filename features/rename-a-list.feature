Feature: Rename a list
  As a user
  I want to rename a list
  So that its title reflects how I work

  Background:
    Given the board app is open

  Scenario: Rename a list
    When I rename the "To Do" list to "Backlog"
    Then a column "Backlog" is visible
    And a column "To Do" is not visible

  Scenario: A blank list name is rejected
    When I rename the "To Do" list to ""
    Then a column "To Do" is visible
