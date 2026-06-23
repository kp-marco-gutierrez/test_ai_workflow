Feature: Add a new list
  As a user
  I want to add a new list to the board
  So that I can organize work into custom stages

  Background:
    Given the board app is open

  Scenario: Add a list to the board
    When I add a list named "Backlog"
    Then a column "Backlog" is visible
    And the board shows 4 columns

  Scenario: A blank list name is rejected
    When I add a list named ""
    Then the board shows 3 columns
    And an error "List name cannot be empty" is shown
