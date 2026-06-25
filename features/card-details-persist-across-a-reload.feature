Feature: Card details persist across a reload
  As a user
  I want a card's label, due date and completion to survive a reload
  So that I never lose my work

  Background:
    Given the board app is open
    And a card "Taxes" is in the "To Do" column

  Scenario: Label, due date and completion all persist
    Given the card "Taxes" has a "red" label
    And the card "Taxes" has the due date "2026-04-15"
    And the card "Taxes" is complete
    When I reload the page
    Then the card "Taxes" has a "red" label
    And the card "Taxes" shows the due date "2026-04-15"
    And the card "Taxes" is shown as complete

  Scenario: A card description persists
    Given the card "Taxes" has the description "File before April"
    When I reload the page
    Then the card "Taxes" shows the description "File before April"
