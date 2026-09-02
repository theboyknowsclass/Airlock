from __future__ import annotations

import json

import aio_pika

from .config import settings

_connection: aio_pika.RobustConnection | None = None
_channel: aio_pika.abc.AbstractChannel | None = None


async def init_queue() -> None:
    global _connection, _channel
    if _connection is None:
        _connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        _channel = await _connection.channel()
        # Durable queue with a dead-letter exchange, matching constitution
        # Principle VIII: bounded retries, then DLQ for ops triage rather
        # than silent loss.
        await _channel.declare_exchange(
            "scan_jobs.dlx", aio_pika.ExchangeType.FANOUT, durable=True
        )
        dlq = await _channel.declare_queue("scan_jobs.dlq", durable=True)
        await dlq.bind("scan_jobs.dlx")
        await _channel.declare_queue(
            settings.scan_queue_name,
            durable=True,
            arguments={"x-dead-letter-exchange": "scan_jobs.dlx"},
        )


async def close_queue() -> None:
    global _connection, _channel
    if _connection is not None:
        await _connection.close()
        _connection = None
        _channel = None


async def publish_scan_job(
    *,
    scan_job_id: str,
    package_id: str,
    ecosystem: str,
    name: str,
    version: str,
    claimed_integrity: str | None,
) -> None:
    if _channel is None:
        raise RuntimeError("Queue channel not initialized — call init_queue() at startup")
    body = json.dumps(
        {
            "scan_job_id": scan_job_id,
            "package_id": package_id,
            "ecosystem": ecosystem,
            "name": name,
            "version": version,
            "claimed_integrity": claimed_integrity,
        }
    ).encode()
    await _channel.default_exchange.publish(
        aio_pika.Message(body=body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
        routing_key=settings.scan_queue_name,
    )
