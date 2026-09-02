from __future__ import annotations

import hashlib
import os
import time
from collections.abc import Callable
from typing import Any

import httpx
import psycopg
import pytest

API_BASE_URL = os.environ.get("AIRLOCK_TEST_API_URL", "http://localhost:8000")
DATABASE_URL = os.environ.get(
    "AIRLOCK_TEST_DATABASE_URL", "postgresql://airlock:airlock@localhost:5432/airlock"
)
DEV_API_KEY = "dev-local-key"  # seeded by README's `make seed` / docker-compose instructions


def wait_until(condition: Callable[[], bool], timeout: float = 30.0, interval: float = 0.5) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(interval)
    raise TimeoutError(f"condition not met within {timeout}s")


@pytest.fixture()
def db() -> psycopg.Connection:
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    # Scenario isolation — each scenario starts from a clean slate. FK
    # order matters: children before parents.
    conn.execute("DELETE FROM requested_packages")
    conn.execute("DELETE FROM package_requests")
    conn.execute("DELETE FROM scan_jobs")
    conn.execute("DELETE FROM packages")
    conn.execute("DELETE FROM build_systems")
    yield conn
    conn.close()


@pytest.fixture()
def api_client(db: psycopg.Connection) -> httpx.Client:
    return httpx.Client(base_url=API_BASE_URL, timeout=10.0)


@pytest.fixture()
def context() -> dict[str, Any]:
    """Shared mutable state between Given/When/Then steps in one scenario."""
    return {}


def seed_build_system(db: psycopg.Connection) -> None:
    key_hash = hashlib.sha256(DEV_API_KEY.encode()).hexdigest()
    db.execute(
        "INSERT INTO build_systems (name, api_key_hash) VALUES ('bdd-test', %s) "
        "ON CONFLICT (name) DO UPDATE SET api_key_hash = EXCLUDED.api_key_hash",
        (key_hash,),
    )
