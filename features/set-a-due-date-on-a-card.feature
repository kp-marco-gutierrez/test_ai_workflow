Feature: Set a due date on a card
  As a user
  I want to set a due date on a card
  So that I know when it is due

  Background:
    Given the board app is open
    And a card "Buy milk" is in the "To Do" column

  Scenario: Set a due date
    When I set the due date of the card "Buy milk" to "2026-07-01"
    Then the card "Buy milk" shows the due date "2026-07-01"

  Scenario: Clear a due date
    Given the card "Buy milk" has the due date "2026-07-01"
    When I clear the due date of the card "Buy milk"
    Then the card "Buy milk" shows no due date
