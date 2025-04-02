import yaml
from pydantic_settings import BaseSettings

class MQSettings(BaseSettings):
    max_retries: int = 3
    retry_delay: float = 1.0
    client_type: str = "MQTT"
    host: str = "mosquitto"
    port: int = 1883
    username: str = ""
    password: str = ""
    topic: str = "caqes"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open("/workspaces/caqes.conf", "r") as f:
            config = yaml.safe_load(f)
            if "mq" in config:
                for key, value in config["mq"].items():
                    setattr(self, key, value)
