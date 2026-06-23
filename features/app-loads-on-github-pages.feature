Feature: App loads on GitHub Pages
  As a visitor
  I want the Trello-lite page to load
  So that I know the app is deployed and running

  Background:
    Given the app page is open

  Scenario: The page loads with the app title
    When the page loads
    Then the document title is "Trello-lite"
    And the heading "Trello-lite" is visible

  Scenario: The board container is present
    When the page loads
    Then a board container is visible
