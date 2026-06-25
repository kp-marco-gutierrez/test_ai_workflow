Feature: Show the label color on a card
  As a user
  I want a labeled card to display its label color
  So that I can scan the board by category

  Background:
    Given the board app is open
    And a card "Buy milk" is in the "To Do" column

  Scenario: Adding a label shows its color on the card
    When I add a "green" label to the card "Buy milk"
    Then the card "Buy milk" shows a "green" label color

  Scenario: Removing the label removes the color
    Given the card "Buy milk" has a "green" label
    When I remove the "green" label from the card "Buy milk"
    Then the card "Buy milk" shows no label color
