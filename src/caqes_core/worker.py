import asyncio
import json
import uuid

from settings.worker_settings import WorkerSettings

from models import Alert

from mq.client_factory import ClientFactory
from mq.message import Message

from quarantine.quarantine_orchestrator import QuarantineOrchestrator
from loggers.audit_logger import get_worker_logger


class Worker:
    def __init__(self, settings = WorkerSettings()) -> None:
        self.worker_id = str(uuid.uuid4())
        self.logger = get_worker_logger(f"caqes.worker{self.worker_id if self.worker_id else ''}")
        self.mq = None
        self.settings = settings
        self.quarantine_orchestrator = QuarantineOrchestrator(self.settings)

    async def run(self) -> None:
        self.logger.info("Starting worker")
        try:
            await self._ensure_connected()

            await self.mq.subscribe("alerts", self._handle_alert)

            # Keep the worker running
            while True:
                await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"Worker error: {e}")
        finally:
            if self.mq:
                await self.mq.close()

    async def _ensure_connected(self) -> None:
        if not self.mq:
            self.logger.debug("Creating new message queue client")
            self.mq = ClientFactory.create(self.settings.mq_client_type)
        if not await self.mq.is_connected():
            try:
                self.logger.info("Attempting to connect to message queue")
                await self.mq.connect()
                self.logger.info("Successfully connected to message queue")
            except Exception as e:
                self.logger.error(f"Failed to connect to message queue: {e}")
                raise e

    async def _handle_alert(self, msg: Message) -> None:
        if not msg.data:
            self.logger.warning("Received empty message")
            await msg.nak()
            raise ValueError("Message data is empty")

        self.logger.debug("Processing new alert message")
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        data = json.loads(msg.data.decode())
        alert = Alert(**data)

        if alert.priority in {"1", "2"}:
            loop.create_task(
                self.quarantine_orchestrator.quarantine(alert))
        await msg.ack()
