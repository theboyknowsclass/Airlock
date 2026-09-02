from __future__ import annotations

import hashlib

from fastapi import Header, HTTPException

from .db import get_pool

# STUB — walking-skeleton scope only. Real auth per constitution §9 is:
#   - build systems: long-lived API key (this is that part, minimally)
#   - humans: OIDC + RBAC (approver role) — NOT implemented here yet.
# The `X-Dev-User` header stands in for an authenticated human identity
# until OIDC is wired up; every use of it is a marker for that follow-up.


async def require_build_system(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="expected 'Bearer <api-key>'")
    api_key = authorization.removeprefix("Bearer ")
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    pool = get_pool()
    row = await pool.fetchrow(
        "SELECT id FROM build_systems WHERE api_key_hash = $1", key_hash
    )
    if row is None:
        raise HTTPException(status_code=401, detail="invalid API key")
    return str(row["id"])


async def require_dev_user(x_dev_user: str = Header(...)) -> str:
    # TODO(OIDC): replace with a real OIDC-authenticated human identity.
    return x_dev_user
