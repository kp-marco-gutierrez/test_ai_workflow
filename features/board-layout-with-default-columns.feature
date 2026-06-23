Feature: Board layout with default columns
  As a user
  I want a board with named columns
  So that I can organize cards into stages

  Background:
    Given the board app is open

  Scenario: Board shows the default columns in order
    When the board loads
    Then the columns "To Do", "Doing", "Done" are visible in that order

  Scenario: Columns start empty
    When the board loads
    Then each column shows 0 cards

  Scenario: The board has a heading
    When the board loads
    Then the page heading is "Trello-lite"
