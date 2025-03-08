
from pydantic_settings import BaseSettings

from mq.client_types import ClientType
from quarantine.quarantine_orchestrator import QuarantineOrchestrator


class WorkerSettings(BaseSettings):
    mq_client_type: ClientType = ClientType.MQTT
    quarantine_orchestrator: QuarantineOrchestrator = QuarantineOrchestrator()
