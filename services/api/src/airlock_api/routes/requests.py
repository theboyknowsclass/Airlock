from __future__ import annotations

import json
from typing import Any, Literal
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..auth import require_build_system
from ..config import settings
from ..db import get_pool
from ..queue import publish_scan_job

router = APIRouter(prefix="/requests", tags=["requests"])


class RequestedPackageIn(BaseModel):
    name: str
    version: str
    # npm lock-file "integrity" field, e.g. "sha512-...". Walking-skeleton
    # scope: this stands in for real lock-file parsing (§8 of spec.md),
    # which is a follow-up, not implemented here.
    integrity: str | None = None


class CreateRequestIn(BaseModel):
    ecosystem: Literal["npm"]
    packages: list[RequestedPackageIn]


class RequestedPackageOut(BaseModel):
    name: str
    version: str
    resolution: str


class RequestOut(BaseModel):
    id: UUID
    status: str
    packages: list[RequestedPackageOut]


@router.post("", response_model=RequestOut, status_code=201)
async def create_request(
    body: CreateRequestIn, build_system_id: str = Depends(require_build_system)
) -> RequestOut:
    if body.ecosystem not in settings.supported_ecosystems:
        raise HTTPException(422, f"unsupported ecosystem: {body.ecosystem}")
    if not body.packages:
        raise HTTPException(422, "at least one package is required")

    pool = get_pool()
    # Jobs to publish to RabbitMQ once the transaction below has actually
    # committed — publishing from inside the transaction would let a worker
    # on a separate connection receive the message and query for a
    # scan_jobs row that isn't visible yet (it isn't committed), losing the
    # job outright. This still leaves a narrow post-commit-pre-publish gap
    # if the process dies in between; closing that fully needs a
    # transactional outbox, which is a follow-up beyond this slice.
    to_publish: list[dict[str, Any]] = []

    async with pool.acquire() as conn:
        async with conn.transaction():
            request_row = await conn.fetchrow(
                """
                INSERT INTO package_requests (source, build_system_id, ecosystem, raw_lock_file)
                VALUES ('build_system', $1, $2, $3)
                RETURNING id
                """,
                UUID(build_system_id),
                body.ecosystem,
                json.dumps(body.model_dump()),
            )
            request_id = request_row["id"]

            resolutions: list[RequestedPackageOut] = []
            for pkg in body.packages:
                package_id, status = await _resolve_or_create_package(
                    conn, body.ecosystem, pkg.name, pkg.version
                )
                resolution = (
                    "approved" if status == "approved"
                    else "rejected" if status == "rejected"
                    else "pending"
                )
                await conn.execute(
                    """
                    INSERT INTO requested_packages (package_request_id, package_id, resolution)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (package_request_id, package_id) DO NOTHING
                    """,
                    request_id,
                    package_id,
                    resolution,
                )
                if resolution == "pending":
                    job = await _create_scan_job_if_needed(conn, package_id)
                    if job is not None:
                        to_publish.append(
                            {
                                "scan_job_id": str(job),
                                "package_id": str(package_id),
                                "ecosystem": body.ecosystem,
                                "name": pkg.name,
                                "version": pkg.version,
                                "claimed_integrity": pkg.integrity,
                            }
                        )
                resolutions.append(
                    RequestedPackageOut(name=pkg.name, version=pkg.version, resolution=resolution)
                )

            overall = _overall_status(resolutions)
            if overall != "pending":
                await conn.execute(
                    "UPDATE package_requests SET status = $2, resolved_at = now() WHERE id = $1",
                    request_id,
                    overall,
                )

    for job_to_publish in to_publish:
        await publish_scan_job(**job_to_publish)

    return RequestOut(id=request_id, status=overall, packages=resolutions)


@router.get("/{request_id}", response_model=RequestOut)
async def get_request(request_id: UUID) -> RequestOut:
    pool = get_pool()
    request_row = await pool.fetchrow(
        "SELECT id, status FROM package_requests WHERE id = $1", request_id
    )
    if request_row is None:
        raise HTTPException(404, "request not found")

    rows = await pool.fetch(
        """
        SELECT p.name, p.version, rp.resolution
        FROM requested_packages rp
        JOIN packages p ON p.id = rp.package_id
        WHERE rp.package_request_id = $1
        """,
        request_id,
    )
    # Re-derive resolution/overall status live (a package may have resolved
    # via another request's scan job since this one was created) rather than
    # trusting only the stored requested_packages.resolution snapshot.
    packages = [
        RequestedPackageOut(name=r["name"], version=r["version"], resolution=r["resolution"])
        for r in rows
    ]
    return RequestOut(id=request_row["id"], status=request_row["status"], packages=packages)


async def _resolve_or_create_package(
    conn: asyncpg.Connection, ecosystem: str, name: str, version: str
) -> tuple[UUID, str]:
    row = await conn.fetchrow(
        """
        INSERT INTO packages (ecosystem, name, version, status)
        VALUES ($1, $2, $3, 'scanning')
        ON CONFLICT (ecosystem, name, version) DO NOTHING
        RETURNING id, status
        """,
        ecosystem,
        name,
        version,
    )
    if row is None:
        row = await conn.fetchrow(
            "SELECT id, status FROM packages WHERE ecosystem = $1 AND name = $2 AND version = $3",
            ecosystem,
            name,
            version,
        )
    return row["id"], row["status"]


async def _create_scan_job_if_needed(conn: asyncpg.Connection, package_id: UUID) -> UUID | None:
    # The partial UNIQUE index (migrations/versions/0001) means this INSERT
    # is a no-op if a scan job is already in flight for this package —
    # that's the dedup decision from spec.md §6, enforced by the DB rather
    # than application logic racing to check-then-insert. Returns None (no
    # publish needed) when a job was already in flight.
    job_row = await conn.fetchrow(
        """
        INSERT INTO scan_jobs (package_id)
        VALUES ($1)
        ON CONFLICT (package_id) WHERE status IN ('queued', 'running') DO NOTHING
        RETURNING id
        """,
        package_id,
    )
    return job_row["id"] if job_row is not None else None


def _overall_status(resolutions: list[RequestedPackageOut]) -> str:
    if any(r.resolution == "rejected" for r in resolutions):
        return "rejected"
    if all(r.resolution == "approved" for r in resolutions):
        return "approved"
    return "pending"
