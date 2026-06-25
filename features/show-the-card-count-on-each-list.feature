Feature: Show the card count on each list
  As a user
  I want each list to show how many cards it has
  So that I can see workload at a glance

  Background:
    Given the board app is open

  Scenario: Count reflects added cards
    When I add a card "A" to the "To Do" column
    And I add a card "B" to the "To Do" column
    Then the "To Do" column header shows a count of 2

  Scenario: Count updates when a card is deleted
    Given a card "A" is in the "To Do" column
    When I delete the card "A"
    Then the "To Do" column header shows a count of 0
