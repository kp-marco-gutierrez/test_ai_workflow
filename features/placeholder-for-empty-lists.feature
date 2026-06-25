Feature: Placeholder for empty lists
  As a user
  I want an empty list to show a friendly placeholder
  So that an empty column does not look broken

  Background:
    Given the board app is open

  Scenario: An empty column shows a placeholder
    When the board loads
    Then the "To Do" column shows the placeholder "No cards yet"

  Scenario: The placeholder disappears once a card is added
    When I add a card "First" to the "To Do" column
    Then the "To Do" column does not show the placeholder "No cards yet"
