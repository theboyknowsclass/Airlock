from __future__ import annotations

import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from .config import settings
from .db import close_pool, get_pool, init_pool
from .scan.integrity import ScanToolingError, run_integrity_check

logger = logging.getLogger("airlock_worker")
logging.basicConfig(level=logging.INFO)


async def handle_message(message: AbstractIncomingMessage) -> None:
    payload = json.loads(message.body)
    scan_job_id = payload["scan_job_id"]
    package_id = payload["package_id"]
    pool = get_pool()

    # Claim the job and bump attempt_count atomically — this is what makes
    # a mid-scan worker crash safe: RabbitMQ redelivers the unacked message
    # to another worker, which re-reads state from here rather than trusting
    # anything held only in this process's memory (constitution Principle VIII).
    job = await pool.fetchrow(
        """
        UPDATE scan_jobs SET status = 'running', started_at = now(), attempt_count = attempt_count + 1
        WHERE id = $1
        RETURNING attempt_count
        """,
        scan_job_id,
    )
    if job is None:
        logger.warning("scan job %s no longer exists — dropping message", scan_job_id)
        await message.ack()
        return

    try:
        findings = await run_integrity_check(
            payload["name"], payload["version"], payload.get("claimed_integrity")
        )
    except ScanToolingError as exc:
        await _handle_scan_failure(message, scan_job_id, job["attempt_count"], str(exc))
        return

    matched = findings["integrity"]["matched"]
    severity = "critical" if matched is False else "low"

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "UPDATE scan_jobs SET status = 'succeeded', finished_at = now() WHERE id = $1",
                scan_job_id,
            )
            await conn.execute(
                """
                UPDATE packages
                SET status = 'pending_review',
                    security_severity = $2,
                    findings = findings || $3::jsonb,
                    updated_at = now()
                WHERE id = $1
                """,
                package_id,
                severity,
                json.dumps(findings),
            )
    await message.ack()
    logger.info("scan job %s succeeded (package %s, severity=%s)", scan_job_id, package_id, severity)


async def _handle_scan_failure(
    message: AbstractIncomingMessage, scan_job_id: str, attempt_count: int, error: str
) -> None:
    pool = get_pool()
    if attempt_count >= settings.max_attempts:
        await pool.execute(
            "UPDATE scan_jobs SET status = 'dead_lettered', last_error = $2, finished_at = now() WHERE id = $1",
            scan_job_id,
            error,
        )
        logger.error(
            "scan job %s DEAD-LETTERED after %s attempts: %s — ops alert required",
            scan_job_id, attempt_count, error,
        )
        # nack without requeue: RabbitMQ routes this to scan_jobs.dlq via the
        # queue's x-dead-letter-exchange (see api's queue.py topology).
        await message.nack(requeue=False)
    else:
        await pool.execute(
            "UPDATE scan_jobs SET status = 'failed', last_error = $2 WHERE id = $1",
            scan_job_id,
            error,
        )
        logger.warning(
            "scan job %s failed (attempt %s/%s): %s",
            scan_job_id, attempt_count, settings.max_attempts, error,
        )
        await message.nack(requeue=True)


async def main() -> None:
    await init_pool()
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=settings.prefetch_count)
        await channel.declare_exchange("scan_jobs.dlx", aio_pika.ExchangeType.FANOUT, durable=True)
        dlq = await channel.declare_queue("scan_jobs.dlq", durable=True)
        await dlq.bind("scan_jobs.dlx")
        queue = await channel.declare_queue(
            settings.scan_queue_name,
            durable=True,
            arguments={"x-dead-letter-exchange": "scan_jobs.dlx"},
        )

        logger.info("worker started, consuming '%s'", settings.scan_queue_name)
        async with queue.iterator() as messages:
            async for message in messages:
                try:
                    await handle_message(message)
                except Exception:
                    logger.exception("unhandled error processing message — nacking for retry")
                    await message.nack(requeue=True)
    await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
