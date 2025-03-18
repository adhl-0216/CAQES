import asyncio
from models.alert import Alert
from quarantine.protocol.protocol_quarantine import ProtocolQuarantine
from settings.worker_settings import WorkerSettings

class QuarantineOrchestrator:
    def __init__(self, settings: WorkerSettings):
        self.protocols = settings.protocols
        self.networks = settings.networks

    async def quarantine(self, alert: Alert) -> None:
        protocol_tasks = [
            self.quarantine_by_protocol(protocol, alert)
            for protocol in self.protocols
        ]
        await asyncio.gather(*protocol_tasks)

    async def quarantine_by_protocol(self, protocol: ProtocolQuarantine, alert: Alert) -> None:
        success = protocol.ban(
            identifier=alert.source_ip,
            identifier_type="peerhost",
            reason=alert.classification
        )
        if not success:
            print(f"Failed to ban {alert.source_ip} via protocol quarantine")

    async def quarantine_by_network(self, network, alert: Alert) -> None:
        pass