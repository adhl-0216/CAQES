import asyncio
import logging
from models import Alert
from quarantine import NetworkIntegration, ProtocolIntegration
from settings import OrchestratorSettings

class QuarantineOrchestrator:
    def __init__(self, settings: OrchestratorSettings):
        self.logger = logging.getLogger("caqes.quarantine.orchestrator")
        self.protocols = settings.protocols
        self.networks = settings.networks
        self.policies = settings.policies

    async def quarantine(self, alert: Alert) -> None:
        self.logger.info(f"Processing quarantine request for alert {alert.alert_id}")
        
        if not self._should_quarantine_alert(alert):
            self.logger.info(f"No matching policies for alert {alert.alert_id}")
            self.logger.debug(f"Alert details: {alert.model_dump()}")
            return

        self.logger.info("Creating quarantine tasks")
        quarantine_tasks = self._create_quarantine_tasks(alert)
        try:
            await asyncio.gather(*quarantine_tasks)
            self.logger.info(f"Quarantine tasks completed for alert {alert.alert_id}")
        except Exception as e:
            self.logger.error(f"Error executing quarantine tasks")
            self.logger.debug(f"Quarantine error details: {str(e)}")
            raise

    def _should_quarantine_alert(self, alert: Alert) -> bool:
        return any(policy.evaluate(alert) for policy in self.policies)

    def _create_quarantine_tasks(self, alert: Alert) -> list:
        protocol_tasks = [
            self._quarantine_by_protocol(protocol, alert)
            for protocol in self.protocols
        ]
        network_tasks = [
            self._quarantine_by_network(network, alert)
            for network in self.networks
        ]
        return protocol_tasks + network_tasks

    async def _quarantine_by_protocol(self, protocol: ProtocolIntegration, alert: Alert) -> None:
        self.logger.debug(f"Executing protocol quarantine for IP {alert.source_ip}")
        try:
            success = protocol.ban(
                ip_address=str(alert.source_ip),
                reason=alert.classification
            )
            if not success:
                self.logger.error("Protocol quarantine operation failed")
        except Exception as e:
            self.logger.error("Exception during protocol quarantine")
            self.logger.debug(f"Protocol quarantine error: {str(e)}")

    async def _quarantine_by_network(self, network: NetworkIntegration, alert: Alert) -> None:
        self.logger.debug(f"Executing network quarantine for IP {alert.source_ip}")
        try:
            success = network.ban(
                ip_address=str(alert.source_ip),
                reason=alert.classification
            )
            if not success:
                self.logger.error("Network quarantine operation failed")
        except Exception as e:
            self.logger.error("Exception during network quarantine")
            self.logger.debug(f"Network quarantine error: {str(e)}")