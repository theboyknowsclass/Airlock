from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Awaitable, Callable, Optional

from pydantic import BaseModel, ConfigDict, Field


MetadataLoader = Callable[[], Awaitable["VersionMetadata"]]


class VersionProviderError(Exception):
    """Base error for version provider failures."""


class VersionNotAvailableError(VersionProviderError):
    """Raised when the version metadata source does not provide data."""


class VersionTimeoutError(VersionProviderError):
    """Raised when retrieving version metadata exceeds the configured timeout."""


class VersionMetadata(BaseModel):
    version: str
    build_timestamp: Optional[datetime] = Field(
        default=None, alias="buildTimestamp"
    )
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        alias="retrievedAt",
    )
    display_label: str = Field(alias="displayLabel")
    source: str = "env"

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: lambda value: value.isoformat()},
    )


class VersionProvider:
    """Fetches version metadata with timeout guarantees."""

    def __init__(
        self,
        timeout_seconds: float = 1.0,
        loader: Optional[MetadataLoader] = None,
    ) -> None:
        self._timeout = timeout_seconds
        self._loader = loader or self._load_from_environment

    async def get_version(self) -> VersionMetadata:
        """Retrieve version metadata or raise a provider error."""
        try:
            metadata = await asyncio.wait_for(
                self._loader(), timeout=self._timeout
            )
        except asyncio.TimeoutError as exc:
            raise VersionTimeoutError(
                "Version lookup exceeded timeout"
            ) from exc
        except VersionProviderError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise VersionProviderError("Unexpected version provider failure") from exc

        return metadata

    async def _load_from_environment(self) -> VersionMetadata:
        version = os.getenv("SERVER_VERSION")
        if not version:
            raise VersionNotAvailableError(
                "SERVER_VERSION environment variable is not set"
            )

        display_label = os.getenv("SERVER_VERSION_LABEL", version)
        source = os.getenv("SERVER_VERSION_SOURCE", "env")
        build_timestamp_raw = os.getenv("SERVER_BUILD_TIMESTAMP")

        build_timestamp: Optional[datetime] = None
        if build_timestamp_raw:
            try:
                build_timestamp = datetime.fromisoformat(build_timestamp_raw)
            except ValueError as exc:
                raise VersionProviderError(
                    "SERVER_BUILD_TIMESTAMP must be ISO 8601 formatted"
                ) from exc

        return VersionMetadata(
            version=version,
            display_label=display_label,
            build_timestamp=build_timestamp,
            source=source,
        )

