Feature: Header controls fit small screens
  As a phone user
  I want the header and its search box to fit the screen
  So that controls are not oversized or cut off

  Background:
    Given the board app is open on a 375px-wide screen

  Scenario: The header content fits the screen
    When the board loads
    Then the header content fits within the screen width

  Scenario: It fits on a very small screen too
    Given the board app is open on a 320px-wide screen
    When the board loads
    Then the header content fits within the screen width
