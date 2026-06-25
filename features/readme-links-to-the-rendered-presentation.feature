Feature: README links to the rendered presentation
  As a reader
  I want the slide-deck link to open the actual presentation
  So that I see the rendered deck, not raw HTML source

  Background:
    Given the project README

  Scenario: The deck link points to the rendered Pages URL
    When I read the slide-deck link
    Then it points to "https://kp-marco-gutierrez.github.io/test_ai_workflow/docs/pipeline-deck.html"
    And it is not the bare repository path "docs/pipeline-deck.html"
