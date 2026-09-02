from __future__ import annotations

import pathlib
import subprocess
import sys
from typing import Any

import httpx
import psycopg
from pytest_bdd import given, parsers, scenarios, then, when

from tests.conftest import DEV_API_KEY, seed_build_system, wait_until

scenarios("../features/package_request.feature")


def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {DEV_API_KEY}"}


@given("a registered build system with a valid API key")
def registered_build_system(db: psycopg.Connection) -> None:
    seed_build_system(db)


@given(parsers.parse('npm package "{name}" version "{version}" is already approved'))
def already_approved_package(db: psycopg.Connection, name: str, version: str) -> None:
    db.execute(
        """
        INSERT INTO packages (ecosystem, name, version, status, approved_by, approved_at)
        VALUES ('npm', %s, %s, 'approved', 'bdd-seed', now())
        """,
        (name, version),
    )


@when(parsers.parse('I request approval for npm package "{name}" version "{version}"'))
def request_approval(api_client: httpx.Client, context: dict[str, Any], name: str, version: str) -> None:
    response = api_client.post(
        "/requests",
        headers=_auth_headers(),
        json={"ecosystem": "npm", "packages": [{"name": name, "version": version}]},
    )
    assert response.status_code == 201, response.text
    context["response"] = response.json()
    context["name"] = name
    context["version"] = version


@when(parsers.parse('the scan job for "{name}" version "{version}" starts running'))
def scan_job_starts_running(db: psycopg.Connection, name: str, version: str) -> None:
    def is_running() -> bool:
        row = db.execute(
            """
            SELECT sj.status FROM scan_jobs sj
            JOIN packages p ON p.id = sj.package_id
            WHERE p.name = %s AND p.version = %s
            ORDER BY sj.queued_at DESC LIMIT 1
            """,
            (name, version),
        ).fetchone()
        return row is not None and row[0] == "running"

    wait_until(is_running, timeout=20.0)


@when("the worker is killed mid-scan and restarted")
def kill_and_restart_worker() -> None:
    # Prefer docker compose (the documented dev workflow) — but only if a
    # compose-managed worker is actually running; `docker compose kill` on
    # an absent service still exits 0, so that alone isn't a reliable
    # signal. Fall back to a plain process kill/restart for a local
    # `python -m airlock_worker.main` dev loop without Docker.
    ps = subprocess.run(
        ["docker", "compose", "ps", "-q", "worker"], cwd=_repo_root(), capture_output=True
    )
    if ps.returncode == 0 and ps.stdout.strip():
        subprocess.run(["docker", "compose", "kill", "worker"], check=True, cwd=_repo_root())
        subprocess.run(["docker", "compose", "up", "-d", "worker"], check=True, cwd=_repo_root())
        return

    pkill = subprocess.run(["pkill", "-9", "-f", "airlock_worker.main"])
    if pkill.returncode != 0:
        raise RuntimeError(
            "could not kill the worker via docker compose or pkill — "
            "is a worker actually running (docker compose, or `python -m airlock_worker.main`)?"
        )
    # Reuses this test process's own interpreter — works when airlock_worker
    # is installed into the same environment as airlock_api's dev deps
    # (a plausible single-venv local dev setup); errors surface to a log
    # file rather than vanishing into DEVNULL, since a silently-failed
    # restart here just looks like a hung test otherwise.
    worker_log = open(_repo_root() / "worker-restart.log", "ab")
    subprocess.Popen(
        [sys.executable, "-m", "airlock_worker.main"],
        cwd=str(_repo_root() / "services" / "worker" / "src"),
        stdout=worker_log,
        stderr=worker_log,
        start_new_session=True,
    )


@then(parsers.parse('the request status is "{status}"'))
def check_request_status(context: dict[str, Any], status: str) -> None:
    assert context["response"]["status"] == status, context["response"]


@then(parsers.parse('the package eventually reaches status "{status}"'))
def package_eventually(db: psycopg.Connection, context: dict[str, Any], status: str) -> None:
    name, version = context["name"], context["version"]

    def has_status() -> bool:
        row = db.execute(
            "SELECT status FROM packages WHERE name = %s AND version = %s", (name, version)
        ).fetchone()
        return row is not None and row[0] == status

    wait_until(has_status, timeout=60.0)


@then(parsers.parse('no scan job is created for "{name}" version "{version}"'))
def no_scan_job(db: psycopg.Connection, name: str, version: str) -> None:
    row = db.execute(
        """
        SELECT count(*) FROM scan_jobs sj
        JOIN packages p ON p.id = sj.package_id
        WHERE p.name = %s AND p.version = %s
        """,
        (name, version),
    ).fetchone()
    assert row is not None and row[0] == 0


@then(parsers.parse('the scan job for "{name}" version "{version}" succeeded on a later attempt'))
def scan_job_succeeded_later(db: psycopg.Connection, name: str, version: str) -> None:
    row = db.execute(
        """
        SELECT sj.status, sj.attempt_count FROM scan_jobs sj
        JOIN packages p ON p.id = sj.package_id
        WHERE p.name = %s AND p.version = %s
        ORDER BY sj.queued_at DESC LIMIT 1
        """,
        (name, version),
    ).fetchone()
    assert row is not None
    status, attempt_count = row
    assert status == "succeeded", f"expected succeeded, got {status}"
    assert attempt_count >= 2, (
        f"expected redelivery to show >=2 attempts after the kill, got {attempt_count} — "
        "the job may have completed before the kill landed"
    )


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[4]
