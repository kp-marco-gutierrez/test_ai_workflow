Feature: Persist the board across reloads
  As a user
  I want my cards to remain after reloading
  So that I do not lose my board

  Background:
    Given the board app is open

  Scenario: A card persists after reload
    Given a card "Buy milk" is in the "To Do" column
    When I reload the page
    Then the "To Do" column contains a card titled "Buy milk"

  Scenario: A card stays in its column after reload
    Given a card "Walk dog" is in the "Doing" column
    When I reload the page
    Then the "Doing" column contains a card titled "Walk dog"
    And the "To Do" column shows 0 cards
