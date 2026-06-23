Feature: Delete a list
  As a user
  I want to delete a list
  So that I can remove stages I no longer use

  Background:
    Given the board app is open

  Scenario: Delete a list from the board
    When I delete the "Done" list
    Then a column "Done" is not visible
    And the board shows 2 columns

  Scenario: Deleting a list removes its cards
    Given a card "Buy milk" is in the "To Do" column
    When I delete the "To Do" list
    Then a column "To Do" is not visible
    And no card titled "Buy milk" is visible
