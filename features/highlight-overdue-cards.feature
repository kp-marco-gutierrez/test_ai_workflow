Feature: Highlight overdue cards
  As a user
  I want overdue cards to be visually marked
  So that I notice late tasks

  Background:
    Given the board app is open

  # Visual indicator: the card element carries the CSS class "overdue"

  Scenario: A past due date marks the card overdue
    Given a card "Pay rent" with due date "2020-01-01" is in the "To Do" column
    When the board loads
    Then the card "Pay rent" has the "overdue" CSS class

  Scenario: A future due date is not overdue
    Given a card "Plan trip" with due date "2999-01-01" is in the "To Do" column
    When the board loads
    Then the card "Plan trip" is visible and does not have the "overdue" CSS class
