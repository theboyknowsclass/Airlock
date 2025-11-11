Feature: Display server version badge
  Background:
    Given the initial site build is available

  Scenario: Version loads successfully
    Given a visitor opens the initial site
    When the client requests the current server version
    Then a loading placeholder is displayed in the bottom-right corner
    And the placeholder is replaced with the server version within one second
    And the server version is announced to assistive technologies

  Scenario: Version request fails
    Given a visitor opens the initial site
    When the client fails to retrieve the server version within one second
    Then the loading placeholder is dismissed
    And an accessible error view replaces the entire page
    And the visitor is prompted with retry guidance

