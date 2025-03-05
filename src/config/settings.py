from pydantic_settings import BaseSettings


class NatsSettings(BaseSettings):
    url: str = "nats://nats:4222"
    max_retries: int = 3
    retry_delay: float = 1.0

    class Config:
        env_prefix = "NATS_"


settings = NatsSettings()
