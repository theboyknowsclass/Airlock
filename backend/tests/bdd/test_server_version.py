from pathlib import Path

import pytest
from pytest_bdd import given, scenario, scenarios, then, when

FEATURE_DIR = Path(__file__).parent / "features"
scenarios(FEATURE_DIR / "server_version.feature")


@given("the version endpoint is exposed publicly")
def version_endpoint_exposed():
    raise NotImplementedError("BDD step pending implementation.")


@when("a client calls GET /api/version")
def client_calls_version_endpoint_success():
    raise NotImplementedError("BDD step pending implementation.")


@when(
    "a client calls GET /api/version and the upstream source is unavailable"
)
def client_calls_version_endpoint_timeout():
    raise NotImplementedError("BDD step pending implementation.")


@then("the server responds with status 200")
def server_responds_with_success_status():
    raise NotImplementedError("BDD step pending implementation.")


@then("the payload contains version metadata and retrieved timestamp")
def payload_contains_version_metadata():
    raise NotImplementedError("BDD step pending implementation.")


@then("the server responds within one second with an error status")
def server_responds_with_timeout_error():
    raise NotImplementedError("BDD step pending implementation.")


@then("the failure is recorded in structured logs")
def failure_recorded_in_logs():
    raise NotImplementedError("BDD step pending implementation.")

