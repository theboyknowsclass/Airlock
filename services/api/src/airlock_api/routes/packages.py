from __future__ import annotations

from typing import Literal
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..auth import require_dev_user
from ..db import get_pool

router = APIRouter(prefix="/packages", tags=["packages"])

# STUB — stands in for the Review UI + role-gated Approver flow (spec.md
# §4 step 7, §9). Any authenticated caller can decide here; there is no
# `approver` role check yet since OIDC/RBAC isn't wired up (see auth.py).


class DecisionIn(BaseModel):
    decision: Literal["approve", "reject"]


class PackageOut(BaseModel):
    id: UUID
    status: str


@router.post("/{package_id}/decision", response_model=PackageOut)
async def decide_package(
    package_id: UUID, body: DecisionIn, actor: str = Depends(require_dev_user)
) -> PackageOut:
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT status FROM packages WHERE id = $1 FOR UPDATE", package_id
            )
            if row is None:
                raise HTTPException(404, "package not found")
            if row["status"] != "pending_review":
                raise HTTPException(
                    409, f"package is '{row['status']}', not awaiting review"
                )

            new_status = "approved" if body.decision == "approve" else "rejected"
            if new_status == "approved":
                await conn.execute(
                    """
                    UPDATE packages
                    SET status = 'approved', approved_by = $2, approved_at = now(), updated_at = now()
                    WHERE id = $1
                    """,
                    package_id,
                    actor,
                )
            else:
                await conn.execute(
                    """
                    UPDATE packages
                    SET status = 'rejected', rejected_by = $2, rejected_at = now(), updated_at = now()
                    WHERE id = $1
                    """,
                    package_id,
                    actor,
                )

            # Cascade to every request line-item referencing this package —
            # a package can be shared across multiple in-flight requests
            # (spec.md §6 dedup).
            await conn.execute(
                "UPDATE requested_packages SET resolution = $2 WHERE package_id = $1",
                package_id,
                new_status,
            )
            await _recompute_affected_requests(conn, package_id)

    return PackageOut(id=package_id, status=new_status)


async def _recompute_affected_requests(conn: asyncpg.Connection, package_id: UUID) -> None:
    request_ids = await conn.fetch(
        "SELECT DISTINCT package_request_id FROM requested_packages WHERE package_id = $1",
        package_id,
    )
    for r in request_ids:
        resolutions = await conn.fetch(
            "SELECT resolution FROM requested_packages WHERE package_request_id = $1",
            r["package_request_id"],
        )
        values = [x["resolution"] for x in resolutions]
        if "rejected" in values:
            overall = "rejected"
        elif all(v == "approved" for v in values):
            overall = "approved"
        else:
            overall = "pending"
        if overall != "pending":
            await conn.execute(
                "UPDATE package_requests SET status = $2, resolved_at = now() "
                "WHERE id = $1 AND status = 'pending'",
                r["package_request_id"],
                overall,
            )
