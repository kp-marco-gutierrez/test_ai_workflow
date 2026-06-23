Feature: Add a card to a column
  As a user
  I want to add a card to a column
  So that I can capture a task on the board

  Background:
    Given the board app is open

  Scenario: Add a card to the To Do column
    When I add a card "Buy milk" to the "To Do" column
    Then the "To Do" column shows 1 card
    And the "To Do" column contains a card titled "Buy milk"

  Scenario: A blank card title is rejected
    When I add a card "" to the "To Do" column
    Then the "To Do" column shows 0 cards
    And an error "Card title cannot be empty" is shown
