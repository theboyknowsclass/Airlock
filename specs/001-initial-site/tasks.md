# Tasks: Initial Site

## Parallel Execution Guidance
- `[P]` tasks can run in parallel when owned by different engineers or automation agents.
- Tasks without `[P]` rely on the completion of preceding tasks.
- Prefer executing all BDD and contract tests before implementing production logic, in line with the constitution’s BDD-first mandate.

## Task List

### Foundation
1. [X] **T001** – Initialize feature branches and toolchains  
   - Ensure branch `001-initial-site` is active, install Node 20 (npm) and Python 3.11 dependencies per `quickstart.md`.  
   - Paths: repo root, `frontend/`, `backend/`  
   - Dependencies: none  

2. [X] **T002** – Configure linting, formatting, and testing scaffolds  
   - Verify ESLint/Prettier/Vitest configs in `frontend/`; MyPy/Flake8/pytest configs in `backend/`; add if missing.  
   - Paths: `frontend/`, `backend/`  
   - Dependencies: T001  

### BDD & Contract Tests (author to fail first)
[X] 3. **T003 [P]** – Author cucumber-js feature and step skeletons for success flow  
   - Encode Gherkin scenario “Version loads successfully” and create failing steps referencing TanStack Query hook placeholders.  
   - Paths: `frontend/tests/bdd/server-version.feature`, `frontend/tests/bdd/steps/`  
   - Dependencies: T002  

[X] 4. **T004 [P]** – Author cucumber-js feature and step skeletons for failure flow  
   - Capture timeout scenario; ensure step definitions assert dedicated error view behavior and loading placeholder.  
   - Paths: `frontend/tests/bdd/server-version.feature`, `frontend/tests/bdd/steps/`  
   - Dependencies: T002  

[X] 5. **T005 [P]** – Write pytest-bdd scenarios mirroring frontend behaviors  
   - Implement background/ scenarios for `GET /api/version`, emphasizing 1-second timeout and logging expectations.  
   - Paths: `backend/tests/bdd/test_server_version.py`  
   - Dependencies: T002  

[X] 6. **T006 [P]** – Scaffold contract test for `GET /api/version`  
   - Use `contracts/version.openapi.yaml` to validate response schema and error handling (503/500).  
   - Paths: `backend/tests/contract/test_version_endpoint.py`  
   - Dependencies: T002  

### Backend Implementation
[X] 7. **T007** – Implement FastAPI endpoint `/api/version`  
   - Create controller under `backend/src/api/version.py` using data model `ServerVersion`; return schema-compliant payload.  
   - Paths: `backend/src/api/version.py`  
   - Dependencies: T005, T006  

[X] 8. **T008** – Add version provider service and timeout enforcement  
   - Build service in `backend/src/services/version_provider.py` that reads build metadata, enforces 1s timeout, and propagates errors.  
   - Paths: `backend/src/services/version_provider.py`  
   - Dependencies: T007  

[X] 9. **T009** – Implement structured logging for fetch failures  
   - Emit `VersionFetchLogEntry` JSON logs in a telemetry module; ensure integrations with FastAPI logging config.  
   - Paths: `backend/src/telemetry/version_logging.py`, `backend/src/api/version.py`  
   - Dependencies: T008  

[X] 10. **T009a** – Enforce HTTPS-only delivery and rate limiting  
    - Configure FastAPI/ASGI middleware (or deployment settings) to require HTTPS, apply rate limits to `/api/version`, and ensure blocked requests produce structured logs.  
    - Paths: `backend/src/app.py`, `backend/src/api/version.py`  
    - Dependencies: T009  

[X] 11. **T010 [P]** – Write backend unit tests for version provider and logging  
    - Validate timeout behavior, schema mapping, and log payloads.  
    - Paths: `backend/tests/unit/test_version_provider.py`, `backend/tests/unit/test_version_logging.py`  
    - Dependencies: T008, T009  

[X] 12. **T010a [P]** – Add backend security tests for HTTPS enforcement and rate limiting  
    - Author pytest integration/unit tests confirming HTTPS enforcement middleware and rate-limit responses/logging.  
    - Paths: `backend/tests/integration/test_security_guards.py`  
    - Dependencies: T009a  

### Frontend Implementation
13. [X] **T011** – Build TanStack Query hook for server version  
    - Implement `useServerVersion` in `frontend/src/hooks/useServerVersion.ts` using Axios with AbortController enforcing 1s timeout and logging to backend on failure.  
    - Dependencies: T003, T004, T010, T010a (ensures backend telemetry and security ready)  

14. [X] **T012** – Create loading placeholder and status components with MUI  
    - Build `ServerVersionPlaceholder` atom and `ServerVersionBadge` molecule ensuring WCAG contrast and `aria-live="polite"`.  
    - Paths: `frontend/src/components/atoms/`, `frontend/src/components/molecules/`  
    - Dependencies: T011  

15. [X] **T013** – Implement error view template  
    - Replace page layout with dedicated error view component on timeout, including focus management and retry action.  
    - Paths: `frontend/src/pages/ErrorView.tsx`, `frontend/src/components/organisms/ErrorLayout.tsx`  
    - Dependencies: T011  

16. [X] **T014 [P]** – Wire version display into initial page template  
    - Integrate hook and components into `frontend/src/pages/InitialSite.tsx`, ensuring layout anchors bottom-right badge.  
    - Dependencies: T012, T013  

17. [X] **T015 [P]** – Frontend unit tests & accessibility assertions  
    - Write co-located Vitest/MSW tests (e.g., `ServerVersionBadge.test.tsx`, `useServerVersion.test.ts`) plus axe-based tests under `frontend/tests/accessibility/` to verify contrast and announcements.  
    - Paths: `frontend/src/**/?(*.)test.ts[x]`, `frontend/tests/accessibility/`  
    - Dependencies: T011-T014  

18. [X] **T015a [P]** – Create Storybook stories for UI components  
19. [X] **T015b [P]** – Add MSW service mocks and Storybook integration  
    - Document `ServerVersionPlaceholder`, `ServerVersionBadge`, and the error view in Storybook with accessibility notes and design tokens.  
    - Paths: `frontend/.storybook/`, `frontend/src/components/**/__stories__`  
    - Dependencies: T012, T013  

### Integration & End-to-End Validation
20. **T016** – Run and fix cucumber-js suite  
    - Execute frontend BDD tests, implement missing step logic until they pass.  
    - Dependencies: T011-T015a  

21. **T017** – Run and fix pytest-bdd suite  
    - Execute backend BDD tests, adjust endpoint/service to satisfy scenarios.  
    - Dependencies: T007-T010  

22. **T018** – Execute contract and integration tests  
    - Run contract tests plus combined frontend-backend smoke tests ensuring 1-second timeout path triggers proper error view.  
    - Dependencies: T016, T017  

### Observability & Accessibility Polish
23. **T019 [P]** – Configure monitoring hooks for log shipping  
    - Ensure application logs integrate with deployment pipeline (structured stdout, optional exporter hook).  
    - Dependencies: T009, T018  

24. **T020 [P]** – Run automated accessibility audits  
    - Execute axe, pa11y, Lighthouse per `quickstart.md`; remediate violations.  
    - Dependencies: T015, T018  

25. **T020a [P]** – Build and execute performance smoke script  
    - Implement `scripts/perf/check-version-latency.ts` (or equivalent) to measure `/api/version` latency (p95 ≤ 250 ms) and capture results for docs/CI.  
    - Paths: `scripts/perf/check-version-latency.ts`, `backend/tests/performance/test_version_endpoint.py`  
    - Dependencies: T018  

26. **T021** – Manual keyboard and screen reader validation  
    - Follow quickstart manual audits; document results and fixes.  
    - Dependencies: T020, T020a  

### Finalization
27. **T022** – Update documentation and quickstart with implementation notes  
    - Record any deviations, update README/quickstart with commands and known limitations, including HTTPS/rate limiting, Storybook coverage, and performance metrics.  
    - Dependencies: T019-T021  

28. **T023** – Final verification and merge readiness review  
    - Confirm BDD, unit, contract, security, performance, and accessibility validations pass; verify structured logs and rate limiting telemetry; prepare PR checklist.  
    - Dependencies: T022  

