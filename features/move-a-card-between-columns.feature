Feature: Move a card between columns
  As a user
  I want to move a card to another column
  So that I can track its progress across stages

  Background:
    Given the board app is open
    And a card "Buy milk" is in the "To Do" column

  Scenario: Move a card to the Doing column
    When I move the card "Buy milk" to the "Doing" column
    Then the "Doing" column contains a card titled "Buy milk"
    And the "To Do" column shows 0 cards

  Scenario: Move a card to the Done column
    When I move the card "Buy milk" to the "Done" column
    Then the "Done" column contains a card titled "Buy milk"
    And the "To Do" column shows 0 cards
