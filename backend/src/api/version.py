from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

from ..services.version_provider import (
    VersionNotAvailableError,
    VersionProvider,
    VersionProviderError,
    VersionTimeoutError,
)
from ..telemetry.version_logging import log_version_failure
from .dependencies import get_version_provider
from ..core.limiter import limiter


router = APIRouter()


def _client_ip_from_request(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


class VersionResponse(BaseModel):
    version: str
    build_timestamp: Any | None = Field(
        default=None, alias="buildTimestamp"
    )
    retrieved_at: Any = Field(alias="retrievedAt")
    display_label: str = Field(alias="displayLabel")
    source: str

    model_config = ConfigDict(populate_by_name=True)


class ErrorResponse(BaseModel):
    error: str
    message: str

    model_config = ConfigDict(populate_by_name=True)


@router.get(
    "/version",
    response_model=VersionResponse,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
@limiter.limit("60/minute")
async def read_version(
    request: Request,
    provider: VersionProvider = Depends(get_version_provider),
) -> dict[str, Any]:
    request_id = request.headers.get("x-request-id") or str(uuid4())
    client_ip = _client_ip_from_request(request)

    try:
        metadata = await provider.get_version()
    except VersionTimeoutError:
        log_version_failure(
            reason="timeout",
            request_id=request_id,
            client_ip=client_ip,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Version lookup timed out.",
        ) from None
    except VersionNotAvailableError:
        log_version_failure(
            reason="not_available",
            request_id=request_id,
            client_ip=client_ip,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Version metadata is currently unavailable.",
        ) from None
    except VersionProviderError:
        log_version_failure(
            reason="provider_failure",
            request_id=request_id,
            client_ip=client_ip,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve server version.",
        ) from None

    return VersionResponse.model_validate(
        metadata.model_dump()
    ).model_dump(by_alias=True)

