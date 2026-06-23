Feature: Rename a card
  As a user
  I want to rename a card
  So that I can correct or update its title

  Background:
    Given the board app is open
    And a card "Buy milk" is in the "To Do" column

  Scenario: Rename a card
    When I rename the card "Buy milk" to "Buy oat milk"
    Then the "To Do" column contains a card titled "Buy oat milk"
    And the "To Do" column shows 1 card

  Scenario: A blank rename is rejected
    When I rename the card "Buy milk" to ""
    Then the "To Do" column contains a card titled "Buy milk"
