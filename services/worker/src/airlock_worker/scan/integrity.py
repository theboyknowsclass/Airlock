from __future__ import annotations

import base64
import hashlib
from typing import Any

import httpx

from ..config import settings


class ScanToolingError(Exception):
    """The scanner itself failed (network, registry outage) — not a finding
    about the package. Per spec.md §4 step 5, this must never be presented
    to the Approver as a scan result; it drives a retry/DLQ instead."""


async def run_integrity_check(
    name: str, version: str, claimed_integrity: str | None
) -> dict[str, Any]:
    tarball_name = name.rsplit("/", maxsplit=1)[-1]  # naive scoped-package handling
    url = f"{settings.npm_registry_url}/{name}/-/{tarball_name}-{version}.tgz"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.content
    except (httpx.HTTPError, httpx.TimeoutException) as exc:
        raise ScanToolingError(f"fetching {url}: {exc}") from exc

    algo, _, _ = (claimed_integrity or "sha512-").partition("-")
    algo = algo or "sha512"
    try:
        digest = hashlib.new(algo, content).digest()
    except ValueError as exc:
        raise ScanToolingError(f"unsupported integrity algorithm '{algo}': {exc}") from exc
    computed = f"{algo}-{base64.b64encode(digest).decode()}"

    return {
        "integrity": {
            "claimed": claimed_integrity,
            "computed": computed,
            "matched": (computed == claimed_integrity) if claimed_integrity else None,
        }
    }
