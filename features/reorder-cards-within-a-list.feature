Feature: Reorder cards within a list
  As a user
  I want to move a card up or down in its list
  So that I can prioritize tasks

  Background:
    Given the board app is open
    And a card "First" is in the "To Do" column
    And a card "Second" is in the "To Do" column

  Scenario: Move a card up
    When I move the card "Second" up in the "To Do" column
    Then the "To Do" column lists "Second" before "First"

  Scenario: Move a card down
    When I move the card "First" down in the "To Do" column
    Then the "To Do" column lists "Second" before "First"
