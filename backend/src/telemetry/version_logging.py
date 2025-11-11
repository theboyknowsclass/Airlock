from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger

LOGGER_NAME = "initial_site.backend.telemetry"

logger = logging.getLogger(LOGGER_NAME)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


def _log(event: str, level: int, **payload: Any) -> None:
    logger.log(level, event, extra={"event": event, **payload})


def log_version_failure(
    *,
    reason: str,
    request_id: str,
    client_ip: str,
    status_code: int,
) -> None:
    _log(
        "VERSION_FETCH_FAILED",
        logging.ERROR,
        requestId=request_id,
        clientIp=client_ip,
        reason=reason,
        statusCode=status_code,
    )


def log_rate_limit_block(
    *,
    request_id: str,
    client_ip: str,
    limit: str,
) -> None:
    _log(
        "VERSION_RATE_LIMIT_BLOCKED",
        logging.WARNING,
        requestId=request_id,
        clientIp=client_ip,
        limit=limit,
    )


def log_https_violation(
    *,
    request_id: str,
    client_ip: str,
) -> None:
    _log(
        "VERSION_HTTPS_ENFORCEMENT",
        logging.WARNING,
        requestId=request_id,
        clientIp=client_ip,
    )

