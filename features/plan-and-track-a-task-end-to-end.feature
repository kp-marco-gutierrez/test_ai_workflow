Feature: Plan and track a task end to end
  As a user
  I want to create, label, schedule and progress a task
  So that the whole workflow holds together

  Background:
    Given the board app is open

  Scenario: A task carries its details through the workflow and a reload
    When I add a card "Launch" to the "To Do" column
    And I add a "green" label to the card "Launch"
    And I set the due date of the card "Launch" to "2026-05-01"
    And I move the card "Launch" to the "Doing" column
    And I reload the page
    Then the "Doing" column contains a card titled "Launch"
    And the card "Launch" has a "green" label
    And the card "Launch" shows the due date "2026-05-01"
