Feature: Package request resolution
  As a build system, I need packages resolved against Airlock's approval
  gateway before I can trust a build's dependencies — proving the
  queue-backed, restart-safe worker architecture (constitution Principle
  VIII) actually holds, not just that the happy path works.

  Background:
    Given a registered build system with a valid API key

  Scenario: An unknown package is scanned before it resolves
    When I request approval for npm package "is-number" version "7.0.0"
    Then the request status is "pending"
    And the package eventually reaches status "pending_review"

  Scenario: An already-approved package resolves without a new scan
    Given npm package "is-odd" version "3.0.1" is already approved
    When I request approval for npm package "is-odd" version "3.0.1"
    Then the request status is "approved"
    And no scan job is created for "is-odd" version "3.0.1"

  Scenario: A worker crash mid-scan does not lose the job
    When I request approval for npm package "kind-of" version "6.0.3"
    And the scan job for "kind-of" version "6.0.3" starts running
    And the worker is killed mid-scan and restarted
    Then the package eventually reaches status "pending_review"
    And the scan job for "kind-of" version "6.0.3" succeeded on a later attempt
