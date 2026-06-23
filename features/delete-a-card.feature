Feature: Delete a card
  As a user
  I want to delete a card
  So that I can remove tasks I no longer need

  Background:
    Given the board app is open
    And a card "Buy milk" is in the "To Do" column

  Scenario: Delete a card from a column
    When I delete the card "Buy milk"
    Then the "To Do" column shows 0 cards

  Scenario: Deleting one card leaves the others
    Given a card "Walk dog" is in the "To Do" column
    When I delete the card "Buy milk"
    Then the "To Do" column shows 1 card
    And the "To Do" column contains a card titled "Walk dog"
