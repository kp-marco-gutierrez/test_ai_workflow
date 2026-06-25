Feature: Filter cards by label
  As a user
  I want to show only cards with a given label
  So that I can focus on a category

  Background:
    Given the board app is open
    And a card "Buy milk" with a "green" label is in the "To Do" column
    And a card "Walk dog" with a "red" label is in the "To Do" column

  Scenario: Show only green-labeled cards
    When I filter by the "green" label
    Then the card "Buy milk" is visible
    And the card "Walk dog" is hidden

  Scenario: Clearing the filter shows all cards
    Given I filter by the "green" label
    When I clear the label filter
    Then the card "Walk dog" is visible
