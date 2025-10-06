<!--
Sync Impact Report:
Version change: 2.0.0 → 2.1.0 (MINOR: Authentication and vulnerability scanning specifications)
Modified principles: Updated authentication and package manager extensibility
Added sections: ADFS authentication specification, Trivy vulnerability scanning
Removed sections: None
Templates requiring updates:
  ✅ .specify/templates/plan-template.md (updated constitution references)
  ✅ .specify/templates/spec-template.md (updated for security focus)
  ✅ .specify/templates/tasks-template.md (updated for TDD and security)
  ⚠️ .specify/templates/commands/*.md (pending review for agent-specific updates)
Follow-up TODOs: Review and update command templates for ADFS and Trivy integration
-->

# Airlock Constitution

## Core Principles

### I. Test-Driven Development (NON-NEGOTIABLE)
**MANDATORY TDD**: All code MUST follow Red-Green-Refactor cycle. Tests written first, 
approved by user, tests fail, then implementation. No exceptions. Every feature, 
service, and component requires comprehensive test coverage before implementation. 
Tests must be located locally with components for easy coverage visibility.

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

### V. Package Manager Extensibility
**NPM-FIRST WITH EXTENSIBILITY**: Initial implementation MUST focus on npm package 
manager with extensible architecture for future NuGet and pip support. Common 
interfaces and abstractions required from the start. Each package manager 
implementation must be pluggable and independently testable. Architecture must 
support seamless addition of new package managers without core changes.

### VI. Container-First Deployment
**CONTAINERIZED ENVIRONMENTS**: All components MUST be containerized with minimal 
differences between dev and production environments. Docker files abstracted 
for environment alignment. External dependencies require mock services in dev 
containers. Configuration management through environment variables and secrets.

## Security Requirements

### Authentication & Authorization
- **ADFS Integration**: Active Directory Federation Services (ADFS) is the primary 
  authentication mechanism for all user access (includes MFA capabilities)
- **OAuth 2 Extensibility**: Authorization architecture MUST be extensible to support 
  any OAuth 2 provider while maintaining ADFS as the initial implementation
- Role-based access control with principle of least privilege
- Session management with secure token handling via ADFS/OAuth 2 providers
- API authentication via ADFS-issued or OAuth 2 JWT tokens with short expiration times

### Data Protection
- All data at rest encrypted using AES-256
- All data in transit encrypted using TLS 1.3
- Sensitive data (API keys, tokens) stored in secure vaults
- Regular security scanning and vulnerability assessments

### Audit & Compliance
- Comprehensive audit logging for all security events
- Immutable audit trails with tamper detection
- Compliance with security frameworks (OWASP, NIST)
- Regular penetration testing and security reviews

### Vulnerability Management
- **Trivy Integration**: Trivy vulnerability scanner MUST be integrated for 
  comprehensive security scanning of containers, dependencies, and code
- Automated vulnerability scanning in CI/CD pipeline
- Zero tolerance for high and critical vulnerabilities
- Regular dependency updates with Trivy validation
- Container image scanning with Trivy before deployment

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
- **Testing**: Vitest with MSW for mocking
- **UI Testing**: Storybook for component testing
- **Code Quality**: ESLint + Prettier with strict rules
- **Architecture**: Atomic Design Pattern (atoms, molecules, organisms, templates, pages)

### Package Management
- **npm (Primary)**: Latest LTS version with security audit enabled, initial focus
- **NuGet (Future)**: Latest stable version with Trivy vulnerability scanning
- **Python/pip (Future)**: pip with Trivy integration for security scanning
- **Dependency Management**: All dependencies pinned to specific versions
- **Security**: Regular dependency updates with Trivy automated security scanning
- **Extensibility**: Architecture must support seamless addition of new package managers

## Development Workflow

### Code Review Process
- All code changes require security review
- TDD compliance verification mandatory
- SOLID principles adherence check
- Security vulnerability scanning
- Performance impact assessment

### Quality Gates
- 100% test coverage for security-critical components
- Zero high/critical security vulnerabilities (Trivy validation)
- All linting and type checking passes
- Performance benchmarks met
- Documentation updated for all public APIs
- ADFS authentication integration validated

### Deployment Pipeline
- Automated testing in containerized environments
- Trivy security scanning at every stage
- Blue-green deployment with rollback capability
- Environment-specific configuration validation
- Monitoring and alerting for security events
- ADFS integration validation in all environments

## Governance

**Constitution Supremacy**: This constitution supersedes all other development 
practices and must be followed without exception. Any deviation requires 
explicit justification and approval from security team.

**Amendment Process**: Constitution amendments require:
1. Security team review and approval
2. Impact assessment on existing codebase
3. Migration plan for any breaking changes
4. Documentation updates across all templates
5. Version increment following semantic versioning

**Compliance Monitoring**: All pull requests and code reviews MUST verify 
constitution compliance. Automated tools will enforce TDD, security scanning, 
and code quality standards. Manual review required for any complexity 
justifications or security exceptions.

**Version**: 2.1.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-01-27