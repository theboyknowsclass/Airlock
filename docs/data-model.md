# Airlock — Data Model

PostgreSQL schema for the entities and state machines in `spec.md`. Columns
that drive lookups, joins, or the state machines are typed/indexed; anything
else (raw scan output, feed payloads, notification config) lives in a
`jsonb` column instead of its own table.

One normalization note not spelled out in `spec.md`: **`ecosystem` is the
registry namespace, not the lock file format.** `package-lock.json` and
`yarn.lock` both resolve to `npm`; `requirements.txt` and `poetry.lock` both
resolve to `pypi`. This matters for correctness — a package pinned via
either npm lock format must hit the same canonical `packages` row, or the
"already approved" short-circuit silently stops working for half your repos.

```sql
-- Machine callers (build systems), authenticated by API key (§9)
CREATE TABLE build_systems (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name          text NOT NULL UNIQUE,
    api_key_hash  text NOT NULL,
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- Application (§3) — owns ApplicationVersions, gives notifications an owner
CREATE TABLE applications (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name                  text NOT NULL UNIQUE,
    owning_team           text NOT NULL,
    repo_url              text,
    notification_config   jsonb NOT NULL DEFAULT '{"in_app": true}',
    created_at            timestamptz NOT NULL DEFAULT now()
);

-- ApplicationVersion (§3) — building → released → retired (§10)
CREATE TYPE application_version_status AS ENUM ('building', 'released', 'retired');

CREATE TABLE application_versions (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id uuid NOT NULL REFERENCES applications(id),
    version        text NOT NULL,               -- build-system-provided identifier
    status         application_version_status NOT NULL DEFAULT 'building',
    released_at    timestamptz,
    retired_at     timestamptz,
    created_at     timestamptz NOT NULL DEFAULT now(),
    UNIQUE (application_id, version)
);

-- LicensePolicy entry (§3, §10) — unclassified → {approved,banned,needs_approval}, reclassifiable
CREATE TYPE license_status AS ENUM ('unclassified', 'approved', 'banned', 'needs_approval');

CREATE TABLE license_policy (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier     text NOT NULL UNIQUE,         -- normalized SPDX id, or raw text if unparseable
    status         license_status NOT NULL DEFAULT 'unclassified',
    classified_by  text,
    classified_at  timestamptz,
    created_at     timestamptz NOT NULL DEFAULT now(),
    updated_at     timestamptz NOT NULL DEFAULT now()
);

-- Package (§3, §10) — the canonical approval-state store, keyed by (ecosystem, name, version)
CREATE TYPE package_status AS ENUM (
    'license_rejected', 'scanning', 'scan_blocked',
    'pending_review', 'approved', 'rejected', 'revoked'
);
CREATE TYPE severity AS ENUM ('low', 'medium', 'high', 'critical');

CREATE TABLE packages (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    ecosystem         text NOT NULL,             -- npm | pypi | nuget | (later) maven
    name              text NOT NULL,
    version           text NOT NULL,
    status            package_status NOT NULL,
    license_policy_id uuid REFERENCES license_policy(id),
    security_severity severity,                  -- worst-of, §7 — null until scanned
    findings          jsonb NOT NULL DEFAULT '{}', -- raw integrity/vuln/malware/license results
    nexus_repo_ref    text,                       -- where it landed in Nexus once approved (§8a)
    approved_by       text,
    approved_at       timestamptz,
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),
    UNIQUE (ecosystem, name, version)
);

-- ScanJob (§3, §10) — queued → running → succeeded/failed → (retry | dead_lettered)
CREATE TYPE scan_job_status AS ENUM ('queued', 'running', 'succeeded', 'failed', 'dead_lettered');

CREATE TABLE scan_jobs (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    package_id    uuid NOT NULL REFERENCES packages(id),
    status        scan_job_status NOT NULL DEFAULT 'queued',
    attempt_count int NOT NULL DEFAULT 0,
    last_error    text,
    queued_at     timestamptz NOT NULL DEFAULT now(),
    started_at    timestamptz,
    finished_at   timestamptz
);
CREATE INDEX ON scan_jobs (package_id) WHERE status IN ('queued', 'running');

-- PackageRequest (§3, §4) — one lock file, one ecosystem, single-source-of-truth for a build's ask
CREATE TYPE request_source AS ENUM ('build_system', 'manual');
CREATE TYPE request_status AS ENUM ('pending', 'approved', 'rejected');

CREATE TABLE package_requests (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source                request_source NOT NULL,
    build_system_id       uuid REFERENCES build_systems(id),   -- set if source = build_system
    requested_by          text,                                -- dev identity if source = manual
    application_version_id uuid REFERENCES application_versions(id), -- null for manual requests
    ecosystem             text NOT NULL,
    status                request_status NOT NULL DEFAULT 'pending',
    raw_lock_file         jsonb NOT NULL,        -- original submission, kept for audit/repro
    created_at            timestamptz NOT NULL DEFAULT now(),
    resolved_at           timestamptz
);

-- RequestedPackage (§3) — one line item within a request
CREATE TYPE requested_package_resolution AS ENUM ('pending', 'approved', 'rejected');

CREATE TABLE requested_packages (
    id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    package_request_id uuid NOT NULL REFERENCES package_requests(id),
    package_id         uuid NOT NULL REFERENCES packages(id),
    resolution         requested_package_resolution NOT NULL DEFAULT 'pending',
    UNIQUE (package_request_id, package_id)
);

-- WatchListEntry (§3, §5) — released version's packages, monitored until retirement
CREATE TABLE watch_list_entries (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    application_version_id  uuid NOT NULL REFERENCES application_versions(id),
    package_id              uuid NOT NULL REFERENCES packages(id),
    created_at              timestamptz NOT NULL DEFAULT now(),
    removed_at              timestamptz,          -- set on version retirement (§5)
    UNIQUE (application_version_id, package_id)
);
-- "Is this package currently watched?" = EXISTS a row here with removed_at IS NULL

-- VulnerabilityAlert (§3, §5) — a feed hit against a watched package
CREATE TYPE vuln_feed_source AS ENUM ('osv', 'nvd', 'github_advisory');

CREATE TABLE vulnerability_alerts (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    package_id   uuid NOT NULL REFERENCES packages(id),
    source       vuln_feed_source NOT NULL,
    external_id  text NOT NULL,                   -- CVE / GHSA id
    severity     severity,
    details      jsonb NOT NULL DEFAULT '{}',      -- raw feed payload
    detected_at  timestamptz NOT NULL DEFAULT now(),
    notified_at  timestamptz
);

-- AuditLogEntry (§3, §9) — every manual decision, append-only
CREATE TABLE audit_log (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    actor       text NOT NULL,                     -- user id, or 'system' for automated entries
    action      text NOT NULL,                      -- e.g. 'package.approve', 'license.reclassify'
    target_type text NOT NULL,
    target_id   uuid NOT NULL,
    rationale   text,
    metadata    jsonb NOT NULL DEFAULT '{}',
    created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON audit_log (target_type, target_id);
```

## Notes

- **`packages.findings`** is the one big JSONB blob — integrity check result,
  vulnerability scan output, malware/behavior scan output. None of it needs
  to be queried directly by the app (the derived `security_severity` column
  is what queues/sorts on); it's there for the Approver's review screen and
  for audit trail, so a blob is the right shape rather than modeling every
  scanner's output as its own table.
- **`raw_lock_file`** on `package_requests` keeps the original submission
  for reproducibility/audit without needing a file store for something this
  small — reconsider as a file/blob reference if lock files turn out to be
  large enough that this bloats the table.
- **License score** isn't a separate column — it's derived from
  `packages.license_policy_id → license_policy.status` at read time, since
  §7 keeps it a distinct, non-blended signal from `security_severity`.
- **`ecosystem` is a plain `text`, not an enum**, deliberately — new
  ecosystems (Maven, later) are additive without a migration; only the
  application-layer parser/adapter list needs updating (§8).
