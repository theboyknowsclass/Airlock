import json
import logging

from backend.src.telemetry.version_logging import (
    logger,
    log_https_violation,
    log_rate_limit_block,
    log_version_failure,
)


def _first_log_record_json(caplog) -> dict:
    assert caplog.records, "Expected at least one log record"
    first_line = caplog.text.strip().splitlines()[0]
    return json.loads(first_line)


def test_log_version_failure(caplog):
    caplog.set_level(logging.INFO, logger=logger.name)

    log_version_failure(
        reason="timeout",
        request_id="req-1",
        client_ip="127.0.0.1",
        status_code=503,
    )

    record = _first_log_record_json(caplog)
    assert record["event"] == "VERSION_FETCH_FAILED"
    assert record["reason"] == "timeout"
    assert record["requestId"] == "req-1"
    assert record["statusCode"] == 503


def test_log_rate_limit_block(caplog):
    caplog.set_level(logging.INFO, logger=logger.name)

    log_rate_limit_block(
        request_id="req-2",
        client_ip="127.0.0.1",
        limit="60/minute",
    )

    record = _first_log_record_json(caplog)
    assert record["event"] == "VERSION_RATE_LIMIT_BLOCKED"
    assert record["limit"] == "60/minute"


def test_log_https_violation(caplog):
    caplog.set_level(logging.INFO, logger=logger.name)

    log_https_violation(request_id="req-3", client_ip="127.0.0.1")

    record = _first_log_record_json(caplog)
    assert record["event"] == "VERSION_HTTPS_ENFORCEMENT"
    assert record["requestId"] == "req-3"

