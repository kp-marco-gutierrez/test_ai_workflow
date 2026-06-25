Feature: README documents the delivery pipeline
  As someone browsing the repository
  I want the README to explain how features are built and shipped
  So that I can understand and trust the pipeline at a glance

  Background:
    Given the repository README

  Scenario: README links to the slide deck
    When I read the README
    Then it contains a link to "docs/pipeline-deck.html"

  Scenario: README shows the pipeline as a Mermaid diagram
    When I read the README
    Then it contains a fenced "mermaid" diagram block
    And the diagram references "Spec", "tests", "review", and "deploy"

  Scenario: README states the core principle
    When I read the README
    Then it explains that AI generates code and deterministic CI decides pass or fail
