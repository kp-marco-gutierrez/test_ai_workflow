Feature: README documents the app, not only the pipeline
  As a reader
  I want the README to explain the Trello-lite app itself
  So that I understand what the tool does, not only how it ships

  Background:
    Given the project README

  Scenario: There is a section describing the Trello-lite app
    When I read the README
    Then it has a section describing the Trello-lite board app
    And that section mentions lists, cards, labels and due dates

  Scenario: It still documents the delivery pipeline
    When I read the README
    Then it still has a section describing the delivery pipeline
