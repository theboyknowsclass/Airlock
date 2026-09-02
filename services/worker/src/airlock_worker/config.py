from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AIRLOCK_")

    database_url: str = "postgresql://airlock:airlock@localhost:5432/airlock"
    rabbitmq_url: str = "amqp://airlock:airlock@localhost:5672/"
    scan_queue_name: str = "scan_jobs"

    # Bounded retries before a job is nacked to the dead-letter queue
    # (constitution Principle VIII) — matches the attempt_count tracked on
    # scan_jobs.
    max_attempts: int = 3

    # npm registry base URL — deliberately not the full "any ecosystem"
    # adapter set from spec.md §8a, just enough to prove the mechanism.
    npm_registry_url: str = "https://registry.npmjs.org"

    prefetch_count: int = 8


settings = Settings()
