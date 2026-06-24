Feature: Mark a card complete
  As a user
  I want to mark a card complete
  So that I can see which tasks are done

  Background:
    Given the board app is open
    And a card "Buy milk" is in the "To Do" column

  Scenario: Mark a card complete
    When I mark the card "Buy milk" complete
    Then the card "Buy milk" is shown as complete

  Scenario: Unmark a completed card
    Given the card "Buy milk" is complete
    When I mark the card "Buy milk" not complete
    Then the card "Buy milk" is shown as not complete
