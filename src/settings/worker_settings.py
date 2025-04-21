from typing import Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from caqes_core.mq import ClientType

class WorkerSettings(BaseSettings):
    client_type: ClientType = ClientType.MQTT
    max_retries: int = 3
    retry_delay: float = 1.0
    host: str = "mosquitto"
    port: int = 1883
    username: str = ""
    password: str = ""
    topic: str = "alerts"

    def __init__(self, config_dict: Dict[str, Any] | None = None, **kwargs):
        if config_dict is not None:
            kwargs = {
                "client_type": config_dict.get("client_type", ClientType.MQTT),
                "max_retries": config_dict.get("max_retries", 3),
                "retry_delay": config_dict.get("retry_delay", 1.0),
                "host": config_dict.get("host", "mosquitto"),
                "port": config_dict.get("port", 1883),
                "username": config_dict.get("username", ""),
                "password": config_dict.get("password", ""),
                "topic": config_dict.get("topic", "alerts")
            }

        super().__init__(**kwargs)

    model_config = SettingsConfigDict(extra="ignore")