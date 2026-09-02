from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AIRLOCK_")

    database_url: str = "postgresql://airlock:airlock@localhost:5432/airlock"
    rabbitmq_url: str = "amqp://airlock:airlock@localhost:5672/"
    scan_queue_name: str = "scan_jobs"

    # Walking-skeleton scope: one ecosystem, no OIDC yet. Real auth (build
    # system client-credentials/API-key rotation, human OIDC + RBAC per
    # constitution §9) is deliberately out of scope for this slice.
    supported_ecosystems: tuple[str, ...] = ("npm",)


settings = Settings()
