<!--
Sync Impact Report:
Version change: 10.0.0 → 10.1.0 (MINOR: Added preferred React library stack guidance)
Modified principles: Technology Standards → Technology Standards
Added sections: None
Removed sections: None
Templates requiring updates:
  ✅ .specify/templates/plan-template.md (React standards expanded)
  ✅ .specify/templates/spec-template.md (no changes needed)
  ✅ .specify/templates/tasks-template.md (no changes needed)
  ⚠️ .specify/templates/commands (directory absent; align future command templates when created)
Follow-up TODOs: None
-->

# Airlock Constitution

## Core Principles

### I. Behavior-Driven Development (NON-NEGOTIABLE)
**MANDATORY BDD**: All validation MUST begin with Cucumber-style scenarios written 
in Gherkin (Given/When/Then) before implementation. Scenarios MUST be authored and 
approved prior to coding, executed to fail first, then drive the implementation 
that satisfies them. Every feature, service, and component requires comprehensive 
BDD coverage aligned with user behaviors. Step definitions and implementation 
reside alongside components for clear traceability between behavior and code.

### II. Security-First Architecture
**SECURITY BY DESIGN**: Every component MUST implement security best practices from 
inception. Input validation, output sanitization, authentication, authorization, 
audit logging, and secure communication protocols are mandatory. Security 
requirements supersede performance optimizations. All external dependencies 
must be vetted and pinned to specific versions.

### III. SOLID & DRY Principles
**CLEAN CODE MANDATE**: Single Responsibility, Open/Closed, Liskov Substitution, 
Interface Segregation, and Dependency Inversion principles MUST be followed. 
Don't Repeat Yourself - refactor legacy code immediately. All code must be 
highly decoupled with clear interfaces and dependency injection.

### IV. Library-First Design
**MODULAR ARCHITECTURE**: Every feature starts as a standalone, self-contained 
library. Libraries MUST be independently testable, documented, and have clear 
purpose. No organizational-only libraries. Each library exposes functionality 
via CLI interface with text in/out protocol (stdin/args → stdout, errors → stderr).

### V. Accessibility-Driven UX (NON-NEGOTIABLE)
**WCAG 2.1 AA COMPLIANCE**: Every user-facing experience MUST meet WCAG 2.1 AA 
criteria at design, development, and deployment. All UX deliverables require 
explicit accessibility acceptance criteria, inclusive copy, and semantic HTML. 
Automated accessibility tests (e.g., axe, pa11y, Lighthouse) MUST run in CI 
pipelines with zero critical violations permitted. Manual keyboard navigation 
and screen reader audits MUST occur before release readiness sign-off.

### VI. Container-First Deployment
**CONTAINERIZED ENVIRONMENTS**: All components MUST be containerized with minimal 
differences between dev and production environments. Docker files abstracted 
for environment alignment. External dependencies require mock services in dev 
containers. Configuration management through environment variables and secrets.

### VII. Minimal Implementation & Clarification-First
**LEAN DELIVERY**: Always prefer the smallest viable change set. Fewer files, 
fewer lines of code, and reuse of existing components are mandatory goals. 
When ambiguity exists, stop and clarify with stakeholders instead of guessing 
or over-specifying. Every implementation MUST demonstrate why additional files 
or abstractions are unavoidable. Speculative extensibility is prohibited.

## Security Requirements

### Authentication & Authorization
- **ADFS Integration**: Active Directory Federation Services (ADFS) is the primary 
  authentication mechanism for all user access (includes MFA capabilities)
- **OAuth 2 Extensibility**: Authorization architecture MUST be extensible to support 
  any OAuth 2 provider while maintaining ADFS as the initial implementation
- Role-based access control with principle of least privilege
- Session management with secure token handling via ADFS/OAuth 2 providers
- API authentication via ADFS-issued or OAuth 2 JWT tokens with short expiration times

## Accessibility Requirements

- WCAG 2.1 AA compliance is mandatory for all user-facing flows, including 
  responsive breakpoints and embedded content
- Design artifacts MUST document accessibility acceptance criteria and include 
  color contrast validation, focus order, and assistive text
- Automated accessibility test suites (axe, pa11y, Lighthouse) MUST execute in 
  CI pipelines and block merges on violations above minor severity
- Keyboard-only and screen reader smoke tests MUST be scripted and executed 
  before release readiness
- Accessibility regressions MUST trigger immediate remediation within the same 
  sprint; deferrals require security and UX lead approval

## Technology Standards

### Python Development
- **Language**: Python 3.11+ (latest LTS)
- **Standards**: PEP8 with 120 character line length
- **Type Checking**: MyPy with strict mode
- **Linting**: Flake8 with security plugins
- **Testing**: pytest with coverage reporting
- **Structure**: Tests in separate `tests/` folder with local component tests

### React/TypeScript Development
- **Language**: TypeScript (latest LTS)
- **Framework**: React 18+ with latest LTS
- **Build Tool**: Vite (latest version)
- **Preferred Libraries**: TanStack Router for routing, TanStack Query for server state, Axios for HTTP client adapters, React Hook Form for form handling, Zustand for lightweight client state, and MUI for component primitives. Any deviation MUST include written justification in the plan.
- **Testing**: Vitest with MSW for mocking
- **UI Testing**: Storybook for component testing
- **Accessibility Testing**: axe-core and Storybook Accessibility add-on with 
  automated WCAG 2.1 AA rule enforcement in CI
- **Code Quality**: ESLint + Prettier with strict rules
- **Architecture**: Atomic Design Pattern (atoms, molecules, organisms, templates, pages)

## Development Workflow

### Code Review Process
- All code changes require security review
- BDD scenario coverage verification mandatory (scenarios exist, fail first, then pass)
- SOLID principles adherence check
- Security vulnerability scanning
- Accessibility compliance verification including automated accessibility test 
  results and manual keyboard/screen reader spot checks
- Performance impact assessment

### Quality Gates
- 100% test coverage for security-critical components
- BDD scenarios implemented for all acceptance criteria and executed in CI
- Zero high/critical security vulnerabilities (Trivy validation)
- All linting and type checking passes
- Performance benchmarks met
- Documentation updated for all public APIs
- ADFS authentication integration validated
- Automated accessibility tests pass with WCAG 2.1 AA conformance and no 
  blockers across supported browsers

**Version**: 10.1.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-11-11