import pytest
from fastapi.testclient import TestClient

from backend.src import create_app


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("SERVER_VERSION", "1.0.0")
    monkeypatch.setenv("SERVER_VERSION_LABEL", "v1.0.0")
    app = create_app()
    return TestClient(app)


def test_https_is_required(client):
    response = client.get("/api/version")
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "https_required"


def test_https_request_succeeds(client):
    response = client.get("/api/version", headers={"x-forwarded-proto": "https"})
    assert response.status_code == 200


def test_rate_limit_enforced(client):
    headers = {"x-forwarded-proto": "https"}
    for _ in range(60):
        client.get("/api/version", headers=headers)

    response = client.get("/api/version", headers=headers)
    assert response.status_code == 429
    assert response.json()["error"] == "rate_limited"

