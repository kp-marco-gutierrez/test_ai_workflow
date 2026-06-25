Feature: Stack columns on small screens
  As a phone user
  I want columns to stack vertically on a narrow screen
  So that the board is not a cramped sideways strip

  Background:
    Given the board app is open on a 375px-wide screen

  Scenario: Columns stack vertically
    When the board loads
    Then the "Doing" column appears below the "To Do" column

  Scenario: A stacked column fills most of the width
    When the board loads
    Then the "To Do" column is at least 90 percent of the screen width
