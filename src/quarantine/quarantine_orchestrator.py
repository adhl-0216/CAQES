import asyncio
import logging
from models.alert import Alert
from quarantine.network.network_quarantine import NetworkQuarantine
from quarantine.protocol.protocol_quarantine import ProtocolQuarantine
from settings.worker_settings import WorkerSettings

class QuarantineOrchestrator:
    def __init__(self, settings: WorkerSettings):
        self.logger = logging.getLogger("caqes.quarantine.orchestrator")
        self.protocols = settings.protocols
        self.networks = settings.networks

    async def quarantine(self, alert: Alert) -> None:
        self.logger.info(f"Starting quarantine process for alert {alert.alert_id}")
        protocol_tasks = [
            self.quarantine_by_protocol(protocol, alert)
            for protocol in self.protocols
        ]
        await asyncio.gather(*protocol_tasks)

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
            print(f"Failed to ban {alert.source_ip} via protocol quarantine")