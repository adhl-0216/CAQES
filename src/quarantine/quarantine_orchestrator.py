import asyncio
import logging
from models import Alert
from quarantine.network.network_quarantine import NetworkQuarantine
from quarantine.protocol.protocol_quarantine import ProtocolQuarantine
from settings.worker_settings import WorkerSettings

class QuarantineOrchestrator:
    def __init__(self, settings: WorkerSettings):
        self.logger = logging.getLogger("caqes.quarantine.orchestrator")
        self.protocols = settings.protocols
        self.networks = settings.networks
        self.policies = settings.policies

    async def quarantine(self, alert: Alert) -> None:
        self.logger.info(f"Starting quarantine process for alert {alert.alert_id}")
        
        if not self._should_quarantine_alert(alert):
            self.logger.info(f"No matching policies for alert {alert.alert_id}, skipping quarantine")
            return

        quarantine_tasks = self._create_quarantine_tasks(alert)
        await asyncio.gather(*quarantine_tasks)

    def _should_quarantine_alert(self, alert: Alert) -> bool:
        return any(policy.evaluate(alert) for policy in self.policies)

    def _create_quarantine_tasks(self, alert: Alert) -> list:
        protocol_tasks = self._create_protocol_tasks(alert)
        network_tasks = self._create_network_tasks(alert)
        return protocol_tasks + network_tasks

    def _create_protocol_tasks(self, alert: Alert) -> list:
        return [
            self.quarantine_by_protocol(protocol, alert)
            for protocol in self.protocols
        ]

    def _create_network_tasks(self, alert: Alert) -> list:
        return [
            self.quarantine_by_network(network, alert)
            for network in self.networks
        ]

    async def quarantine_by_protocol(self, protocol: ProtocolQuarantine, alert: Alert) -> None:
        self.logger.debug(f"Executing protocol quarantine for IP {alert.source_ip}")
        success = protocol.ban(
            ip_address=alert.source_ip,
            reason=alert.classification
        )
        if not success:
            self.logger.error(f"Failed to ban {alert.source_ip} via protocol quarantine")

    async def quarantine_by_network(self, network: NetworkQuarantine, alert: Alert) -> None:
        success = network.ban(
        identifier=alert.source_ip,
        identifier_type="peerhost",
        reason=alert.classification
        )
        if not success:
            self.logger.error(f"Failed to ban {alert.source_ip} via protocol quarantine")