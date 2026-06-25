Feature: README links to the live Trello-lite site
  As a reader
  I want a link to the running app
  So that I can try Trello-lite in my browser

  Background:
    Given the project README

  Scenario: The README links to the live site
    When I read the README
    Then it links to "https://kp-marco-gutierrez.github.io/test_ai_workflow/"
    And the link is labelled as the live Trello-lite app
