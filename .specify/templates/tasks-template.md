# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Accessibility: automated audits, manual verification
   → Polish: unit tests, performance, docs
   → Minimal additions only: skip tasks that introduce new files when existing assets suffice
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
   → Any task that adds a file/code path must justify why reuse is impossible
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 3.1: Setup
- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
**SECURITY: All security-critical components require comprehensive test coverage**
- [ ] T004 [P] Contract test POST /api/users in tests/contract/test_users_post.py
- [ ] T005 [P] Contract test GET /api/users/{id} in tests/contract/test_users_get.py
- [ ] T006 [P] Integration test user registration in tests/integration/test_registration.py
- [ ] T007 [P] Integration test auth flow in tests/integration/test_auth.py
- [ ] T008 [P] Security test authentication bypass in tests/security/test_auth_bypass.py
- [ ] T009 [P] Security test input validation in tests/security/test_input_validation.py
- [ ] T010 [P] Automated accessibility regression test suite in tests/accessibility/axe.spec.ts

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T011 [P] User model in src/models/user.py
- [ ] T012 [P] UserService CRUD in src/services/user_service.py
- [ ] T013 [P] CLI --create-user in src/cli/user_commands.py
- [ ] T014 POST /api/users endpoint
- [ ] T015 GET /api/users/{id} endpoint
- [ ] T016 Input validation with security checks
- [ ] T017 Error handling and security logging
- [ ] T018 Authentication middleware implementation
- [ ] T019 Authorization service implementation

## Phase 3.4: Integration
- [ ] T020 Connect UserService to DB with encryption
- [ ] T021 Security middleware integration
- [ ] T022 Request/response logging with audit trails
- [ ] T023 CORS and security headers
- [ ] T024 Container configuration for dev/prod environments

## Phase 3.5: Polish
- [ ] T025 [P] Unit tests for validation in tests/unit/test_validation.py
- [ ] T026 Performance tests (<200ms)
- [ ] T027 [P] Update docs/api.md
- [ ] T028 Remove duplication (DRY principle)
- [ ] T029 Security vulnerability scanning
- [ ] T030 Run manual-testing.md
- [ ] T031 Manual accessibility audit (keyboard navigation + screen reader smoke tests)

## Dependencies
- Tests (T004-T010) before implementation (T011-T019)
- T011 blocks T012, T020
- T018 blocks T021
- T019 blocks T021
- Implementation before polish (T025-T031)

## Parallel Example
```
# Launch T004-T009 together (all tests):
Task: "Contract test POST /api/users in tests/contract/test_users_post.py"
Task: "Contract test GET /api/users/{id} in tests/contract/test_users_get.py"
Task: "Integration test registration in tests/integration/test_registration.py"
Task: "Integration test auth in tests/integration/test_auth.py"
Task: "Security test authentication bypass in tests/security/test_auth_bypass.py"
Task: "Security test input validation in tests/security/test_input_validation.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing (TDD MANDATORY)
- Security tests must be comprehensive and pass
- Default to reusing existing files; if a new file is unavoidable, note the rationale in the task
- Commit after each task
- Avoid: vague tasks, same file conflicts
- All security-critical components require dedicated security tests

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Relationships → service layer tasks
   
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [ ] All contracts have corresponding tests
- [ ] All entities have model tasks
- [ ] All tests come before implementation (TDD compliance)
- [ ] Security tests included for all security-critical components
- [ ] Accessibility tests (automated + manual) included and scheduled before release
- [ ] Parallel tasks truly independent
- [ ] Each task specifies exact file path
- [ ] No task modifies same file as another [P] task
- [ ] Container configuration tasks included
- [ ] Security scanning and vulnerability assessment tasks included
- [ ] Every task reflects the minimum necessary change; extra scope justified