# Phase 0 Research: Initial Site

## Decision Log
Decision: Use React 18 with TypeScript via Vite for the initial site shell.  
Rationale: Aligns with constitution React/TypeScript standard, delivers fast dev experience, and keeps bundle minimal for a single-page surface.  
Alternatives considered: Next.js (introduces routing/server rendering overhead), Static HTML with vanilla JS (hurts scalability and testability).

Decision: Serve the landing page from a Python 3.11 FastAPI backend that also exposes `/api/version`.  
Rationale: Matches constitution Python standard, keeps API and static hosting co-located, and simplifies containerization.  
Alternatives considered: Node/Express service (diverges from mandated stack), CDN-only static hosting (cannot log failures server-side).

Decision: Enforce the one-second timeout by wrapping `fetch` with `AbortController` on the client and mirroring server-side timeout guards.  
Rationale: Deterministically fulfills requirement to fail fast, avoids dangling responses, and keeps implementation SOLID.  
Alternatives considered: Manual `setTimeout` state flips (risks race conditions), relying solely on server-side timeouts (no client guarantee).

Decision: Render a dedicated, full-page accessible error view with WCAG-compliant contrast, focus trap release, and retry controls.  
Rationale: Meets accessibility mandate, provides clear user recovery guidance, and isolates error UI from main layout for maintainability.  
Alternatives considered: Inline toast notifications (low visibility for assistive tech), silent failure (violates requirement).

Decision: Record fetch failures in the backend application logger (structured JSON to stdout).  
Rationale: Provides centralized operational visibility while remaining lightweight for containerized deployment.  
Alternatives considered: External log aggregation (premature without requirements), client-only console logging (lost in production).

Decision: Use `@cucumber/cucumber` (frontend) and `pytest-bdd` (backend) to author Gherkin scenarios before implementation.  
Rationale: Satisfies constitution BDD mandate, keeps scenarios close to components, and leverages widely supported tooling.  
Alternatives considered: Manual test plans (non-executable), bespoke test harness (unnecessary maintenance).

Decision: Adopt TanStack Query with Axios for the version fetch while omitting TanStack Router, React Hook Form, and Zustand.  
Rationale: Aligns with the preferred React stack for server state management and HTTP calls; routing, form handling, and global client state libraries are not required for a single static view with no inputs.  
Alternatives considered: Raw `fetch` without caching (less resilient to retries), introducing routing/state libraries without need (violates minimalism).

