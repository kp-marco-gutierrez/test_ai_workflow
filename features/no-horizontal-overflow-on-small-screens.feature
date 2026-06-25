Feature: No horizontal overflow on small screens
  As a phone user
  I want the page to fit the screen width
  So that I never scroll sideways to reach controls

  Background:
    Given the board app is open on a 375px-wide screen

  Scenario: The page does not scroll horizontally
    When the board loads
    Then the page has no horizontal scrolling

  Scenario: It still fits on a very small screen
    Given the board app is open on a 320px-wide screen
    When the board loads
    Then the page has no horizontal scrolling
