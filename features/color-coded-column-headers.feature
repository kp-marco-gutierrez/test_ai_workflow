Feature: Color-coded column headers
  As a user
  I want each default column to have its own accent color
  So that I can tell columns apart at a glance

  Background:
    Given the board app is open

  Scenario: To Do and Doing have distinct accents
    When the board loads
    Then the "To Do" column header has the accent "todo"
    And the "Doing" column header has the accent "doing"

  Scenario: Done has its own accent
    When the board loads
    Then the "Done" column header has the accent "done"
