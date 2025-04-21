from typing import List, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from quarantine import NetworkIntegration, ProtocolIntegration, integration_factory
from models.policy import Policy
from policies import PolicyEvaluator

class OrchestratorSettings(BaseSettings):
    networks_config: List[dict] = Field(default_factory=list, description="List of network quarantine configs")
    protocols_config: List[dict] = Field(default_factory=list, description="List of protocol quarantine configs")
    policies_config: List[Policy] = Field(default_factory=list, description="List of policy configurations")

    def __init__(self, config_dict: Dict[str, Any] | None = None, **kwargs):
        if config_dict is not None:
            kwargs = {
                "networks_config": config_dict.get("network", []),
                "protocols_config": config_dict.get("protocol", []),
                "policies_config": [Policy(**p) for p in config_dict.get("policies", [])]
            }

        super().__init__(**kwargs)

    @property
    def networks(self) -> List[NetworkIntegration]:
        return [
            integration_factory.create(
                "network",
                module_type=config["type"],
                **{k: v for k, v in config.items() if k != "type"}
            )
            for config in self.networks_config
        ]

    @property
    def protocols(self) -> List[ProtocolIntegration]:
        return [
            integration_factory.create(
                "protocol", 
                module_type=config["type"],
                **{k: v for k, v in config.items() if k != "type"}
            )
            for config in self.protocols_config
        ]

    @property
    def policies(self) -> List[PolicyEvaluator]:
        return [PolicyEvaluator(policy_config) for policy_config in self.policies_config]

    model_config = SettingsConfigDict(extra="ignore")