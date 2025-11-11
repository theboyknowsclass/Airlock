# Quickstart: Initial Site Feature

## Prerequisites
- Node.js 20.x with npm
- Python 3.11 with uv or pip
- Docker (for container parity)

## Setup
```bash
# Frontend (run from repo root)
npm install --prefix frontend

# Backend
uv pip install -r backend/requirements-dev.txt
```

## Behavior-Driven Development Workflow
All delivery starts with Gherkin scenarios. Author and execute the scenarios below before implementing production code.

```gherkin
Feature: Display server version on the initial site
  Background:
    Given the server provides a public GET /api/version endpoint

  Scenario: Version loads successfully
    Given a visitor opens the initial site
    When the client requests the server version
    Then a loading placeholder is announced in the bottom-right corner
    And the placeholder is replaced with the server version within one second

  Scenario: Version request fails
    Given a visitor opens the initial site
    When the client fails to retrieve the server version within one second
    Then the entire page switches to an accessible error view
    And the visitor is prompted to retry or contact support
```

### Run BDD Suites
```bash
# Frontend cucumber-js suite
npm run -w frontend test:bdd

# Backend pytest-bdd suite
uv run pytest tests/bdd
```
Scenarios must fail before implementation begins, then be driven to pass alongside code changes.

## Accessibility Regression Checks
```bash
# Frontend accessibility smoke (axe + Storybook)
npm run -w frontend test:a11y

# End-to-end keyboard audit script
npm run -w frontend test:keyboard
```

# Component Unit Tests
- Component and hook tests live alongside their source files using the `*.test.ts(x)` convention (e.g., `ServerVersionBadge.test.tsx`).
- Run all co-located Vitest suites:
  ```bash
  npm run -w frontend test
  ```

## Storybook Component Review
```bash
# Launch Storybook with accessibility addons
npm run -w frontend storybook
```
Use Storybook to document `ServerVersionPlaceholder`, `ServerVersionBadge`, and the error view; verify WCAG notes and design tokens before merging UI changes.

## Performance Smoke Test
```bash
# Measure /api/version latency (p95 ≤ 250 ms) from repo root
npx ts-node scripts/perf/check-version-latency.ts
```
Ensure results are captured for CI and referenced in documentation.

## Fast Feedback Loop
```bash
# Frontend dev server with strict type-checking
npm run -w frontend dev -- --strictPort

# Backend auto-reload service
uv run uvicorn backend.src.main:app --reload --port 8080
```

## Verification Prior to Merge
- All cucumber scenarios passing (frontend + backend)
- Vitest unit coverage ≥ 90% on new code
- pytest (unit/integration) coverage ≥ 90% on backend modules
- axe, pa11y, Lighthouse audits show zero critical issues
- Structured logs confirm version fetch success and timeout telemetry

