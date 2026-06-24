Feature: Add a description to a card
  As a user
  I want to add a description to a card
  So that I can capture details about the task

  Background:
    Given the board app is open
    And a card "Buy milk" is in the "To Do" column

  Scenario: Add a description to a card
    When I open the card "Buy milk"
    And I set the description to "Get the oat one"
    Then the card "Buy milk" shows the description "Get the oat one"

  Scenario: A card with no description shows none
    When I open the card "Buy milk"
    Then the card "Buy milk" shows no description
