Feature: Add a color label to a card
  As a user
  I want to add a colored label to a card
  So that I can categorize it visually

  Background:
    Given the board app is open
    And a card "Buy milk" is in the "To Do" column

  Scenario: Add a label to a card
    When I add a "green" label to the card "Buy milk"
    Then the card "Buy milk" has a "green" label

  Scenario: Remove a label from a card
    Given the card "Buy milk" has a "green" label
    When I remove the "green" label from the card "Buy milk"
    Then the card "Buy milk" has no labels
