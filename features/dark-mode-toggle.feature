Feature: Dark mode toggle
  As a user
  I want to switch the board to a dark theme
  So that it is easier on the eyes

  Background:
    Given the board app is open

  Scenario: Toggle to dark mode
    When I click the theme toggle
    Then the page is in dark mode

  Scenario: The chosen theme persists after reload
    Given I click the theme toggle
    When I reload the page
    Then the page is in dark mode
