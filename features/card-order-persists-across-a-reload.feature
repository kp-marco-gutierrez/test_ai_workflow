Feature: Card order persists across a reload
  As a user
  I want my card ordering to survive a reload
  So that my prioritization sticks

  Background:
    Given the board app is open
    And a card "First" is in the "To Do" column
    And a card "Second" is in the "To Do" column

  Scenario: Reordered cards keep their order after reload
    Given I move the card "Second" up in the "To Do" column
    When I reload the page
    Then the "To Do" column lists "Second" before "First"

  Scenario: Order is unchanged when nothing is reordered
    When I reload the page
    Then the "To Do" column lists "First" before "Second"
