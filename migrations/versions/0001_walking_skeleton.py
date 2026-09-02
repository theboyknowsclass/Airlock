"""walking skeleton: build_systems, packages, scan_jobs, package_requests, requested_packages

Subset of docs/data-model.md needed to prove the queue-backed, restart-safe
worker architecture (constitution Principle VIII) end to end: npm ecosystem,
integrity check only. license_policy, applications, watch list, and audit
log are deliberately out of scope for this slice and come in a later
migration.

Revision ID: 0001
Revises:
Create Date: 2026-09-02
"""
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")  # gen_random_uuid()

    op.execute(
        """
        CREATE TABLE build_systems (
            id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name          text NOT NULL UNIQUE,
            api_key_hash  text NOT NULL,
            created_at    timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TYPE package_status AS ENUM (
            'scanning', 'scan_blocked', 'pending_review', 'approved', 'rejected'
        )
        """
    )
    op.execute("CREATE TYPE severity AS ENUM ('low', 'medium', 'high', 'critical')")

    op.execute(
        """
        CREATE TABLE packages (
            id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            ecosystem         text NOT NULL,
            name              text NOT NULL,
            version           text NOT NULL,
            status            package_status NOT NULL,
            security_severity severity,
            findings          jsonb NOT NULL DEFAULT '{}',
            approved_by       text,
            approved_at       timestamptz,
            rejected_by       text,
            rejected_at       timestamptz,
            created_at        timestamptz NOT NULL DEFAULT now(),
            updated_at        timestamptz NOT NULL DEFAULT now(),
            UNIQUE (ecosystem, name, version)
        )
        """
    )

    op.execute(
        """
        CREATE TYPE scan_job_status AS ENUM (
            'queued', 'running', 'succeeded', 'failed', 'dead_lettered'
        )
        """
    )

    op.execute(
        """
        CREATE TABLE scan_jobs (
            id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            package_id    uuid NOT NULL REFERENCES packages(id),
            status        scan_job_status NOT NULL DEFAULT 'queued',
            attempt_count int NOT NULL DEFAULT 0,
            last_error    text,
            queued_at     timestamptz NOT NULL DEFAULT now(),
            started_at    timestamptz,
            finished_at   timestamptz
        )
        """
    )
    # Enforces the dedup decision (spec.md §6) at the DB level: at most one
    # in-flight scan job per package.
    op.execute(
        """
        CREATE UNIQUE INDEX scan_jobs_one_in_flight_per_package
        ON scan_jobs (package_id) WHERE status IN ('queued', 'running')
        """
    )

    op.execute("CREATE TYPE request_source AS ENUM ('build_system', 'manual')")
    op.execute("CREATE TYPE request_status AS ENUM ('pending', 'approved', 'rejected')")

    op.execute(
        """
        CREATE TABLE package_requests (
            id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            source            request_source NOT NULL,
            build_system_id   uuid REFERENCES build_systems(id),
            requested_by      text,
            ecosystem         text NOT NULL,
            status            request_status NOT NULL DEFAULT 'pending',
            raw_lock_file     jsonb NOT NULL,
            created_at        timestamptz NOT NULL DEFAULT now(),
            resolved_at       timestamptz
        )
        """
    )

    op.execute(
        """
        CREATE TABLE requested_packages (
            id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            package_request_id uuid NOT NULL REFERENCES package_requests(id),
            package_id         uuid NOT NULL REFERENCES packages(id),
            resolution         text NOT NULL DEFAULT 'pending',
            UNIQUE (package_request_id, package_id)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE requested_packages")
    op.execute("DROP TABLE package_requests")
    op.execute("DROP TYPE request_status")
    op.execute("DROP TYPE request_source")
    op.execute("DROP TABLE scan_jobs")
    op.execute("DROP TYPE scan_job_status")
    op.execute("DROP TABLE packages")
    op.execute("DROP TYPE severity")
    op.execute("DROP TYPE package_status")
    op.execute("DROP TABLE build_systems")
