from __future__ import annotations

from pathlib import Path

import jsonschema
import pytest
import yaml
from fastapi.testclient import TestClient

from backend.src import create_app

SCHEMA_PATH = (
    Path(__file__)
    .resolve()
    .parents[3]
    / "specs"
    / "001-initial-site"
    / "contracts"
    / "version.openapi.yaml"
)


@pytest.fixture(scope="session")
def version_contract_schema():
    with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        openapi_document = yaml.safe_load(handle)
    return openapi_document["components"]["schemas"]["ServerVersionResponse"]


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("SERVER_VERSION", "1.0.0")
    monkeypatch.setenv("SERVER_VERSION_LABEL", "v1.0.0")
    app = create_app()
    return TestClient(app)


def test_version_endpoint_contract(version_contract_schema, client):
    response = client.get("/api/version", headers={"x-forwarded-proto": "https"})
    assert response.status_code == 200
    payload = response.json()
    jsonschema.validate(instance=payload, schema=version_contract_schema)

