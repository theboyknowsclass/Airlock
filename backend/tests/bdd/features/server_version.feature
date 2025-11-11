Feature: Retrieve server version metadata
  Background:
    Given the version endpoint is exposed publicly

  Scenario: Version request succeeds
    When a client calls GET /api/version
    Then the server responds with status 200
    And the payload contains version metadata and retrieved timestamp

  Scenario: Version request times out
    When a client calls GET /api/version and the upstream source is unavailable
    Then the server responds within one second with an error status
    And the failure is recorded in structured logs

