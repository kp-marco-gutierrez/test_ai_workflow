Feature: Filter cards by a search term
  As a user
  I want to filter cards by title
  So that I can find a card quickly

  Background:
    Given the board app is open
    And a card "Buy milk" is in the "To Do" column
    And a card "Walk dog" is in the "To Do" column

  Scenario: Matching cards stay visible, others hide
    When I search for "milk"
    Then the card "Buy milk" is visible
    And the card "Walk dog" is hidden

  Scenario: Clearing the search shows all cards
    Given I search for "milk"
    When I clear the search
    Then the card "Walk dog" is visible
