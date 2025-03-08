from pydantic_settings import BaseSettings


class MQSettings(BaseSettings):
    max_retries: int = 3
    retry_delay: float = 1.0

    host: str = "mosquitto"
    port: int = 1883
    username: str = ""
    password: str = ""
    topic: str = "caqes"
