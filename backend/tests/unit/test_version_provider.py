import asyncio
from datetime import datetime, timezone

import pytest

from backend.src.services.version_provider import (
    VersionMetadata,
    VersionNotAvailableError,
    VersionProvider,
    VersionTimeoutError,
)


@pytest.mark.asyncio
async def test_get_version_returns_metadata(monkeypatch):
    monkeypatch.setenv("SERVER_VERSION", "1.2.3")
    monkeypatch.setenv("SERVER_VERSION_LABEL", "v1.2.3")
    monkeypatch.setenv(
        "SERVER_BUILD_TIMESTAMP", "2025-11-11T15:00:00+00:00"
    )
    provider = VersionProvider()

    metadata = await provider.get_version()

    assert metadata.version == "1.2.3"
    assert metadata.display_label == "v1.2.3"
    assert metadata.source == "env"
    assert metadata.build_timestamp == datetime(
        2025, 11, 11, 15, 0, tzinfo=timezone.utc
    )
    assert isinstance(metadata.retrieved_at, datetime)


@pytest.mark.asyncio
async def test_get_version_missing_env(monkeypatch):
    monkeypatch.delenv("SERVER_VERSION", raising=False)
    provider = VersionProvider()

    with pytest.raises(VersionNotAvailableError):
        await provider.get_version()


@pytest.mark.asyncio
async def test_get_version_timeout(monkeypatch):
    async def slow_loader():
        await asyncio.sleep(0.05)
        return VersionMetadata(
            version="x",
            display_label="x",
            build_timestamp=None,
            source="test",
        )

    provider = VersionProvider(timeout_seconds=0.01, loader=slow_loader)

    with pytest.raises(VersionTimeoutError):
        await provider.get_version()

