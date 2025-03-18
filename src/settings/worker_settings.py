from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import yaml
from pathlib import Path
from mq.client_types import ClientType
from quarantine.protocol.protocol_quarantine import ProtocolQuarantine

class WorkerSettings(BaseSettings):
    """Main worker settings with dynamic protocol and network configurations."""
    mq_client_type: ClientType = ClientType.MQTT
    networks: List[str] = []
    protocols_config: List[dict] = Field(default_factory=list, description="List of protocol quarantine configs")

    @property
    def protocols(self) -> List[ProtocolQuarantine]:
        """Dynamically instantiate protocol quarantine modules from config."""
        return [
            ProtocolQuarantine.create(
                module_type=config["type"],
                **{k: v for k, v in config.items() if k != "type"}
            )
            for config in self.protocols_config
        ]

    @classmethod
    def from_yaml(cls, path: str = "caqes.conf") -> "WorkerSettings":
        """Load settings from a YAML config file."""
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file {path} not found")

        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}

        return cls(
            mq_client_type=config_data.get("mq_client_type", ClientType.MQTT),
            networks=config_data.get("networks", []),
            protocols_config=config_data.get("protocols", [])
        )

    model_config = SettingsConfigDict(
        extra="ignore"
    )