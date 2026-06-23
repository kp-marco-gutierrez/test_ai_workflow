Feature: Drag a card to another column
  As a user
  I want to drag a card onto another column
  So that I can move it directly without using the dropdown

  Background:
    Given the board app is open
    And a card "Buy milk" is in the "To Do" column

  Scenario: Drag a card to the Doing column
    When I drag the card "Buy milk" onto the "Doing" column
    Then the "Doing" column contains a card titled "Buy milk"
    And the "To Do" column shows 0 cards

  Scenario: Drag a card to the Done column
    When I drag the card "Buy milk" onto the "Done" column
    Then the "Done" column contains a card titled "Buy milk"
    And the "To Do" column shows 0 cards
