import asyncio
import json
import logging
import secrets

from settings import WorkerSettings

from models import Alert

from caqes_core.mq.client_factory import ClientFactory as MqClientFactory
from caqes_core.mq.message import Message
from caqes_core.mq.client import Client as MqClient

from quarantine.quarantine_orchestrator import QuarantineOrchestrator

class Worker:
    def __init__(self, settings: WorkerSettings , orchestrator: QuarantineOrchestrator) -> None:
        self.worker_id = secrets.token_hex(4)
        self.logger = logging.getLogger(f"caqes.worker-{self.worker_id}")
        self.mq : MqClient = None
        self.settings = settings
        self.quarantine_orchestrator = orchestrator

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
            self.mq = MqClientFactory.create(self.settings.client_type, self.settings)
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
        try:
            alert = Alert(**data)
            self.logger.info(f"Created alert object with ID {alert.alert_id}")
            self.logger.debug(f"Alert details: {alert.model_dump()}")
        except Exception as e:
            self.logger.error("Failed to parse alert data")
            self.logger.debug(f"Parse error: {str(e)}")
            self.logger.debug(f"Raw data: {data}")
            await msg.nak()
            return

        if alert:
            self.logger.info(f"Scheduling quarantine task for alert {alert.alert_id}")
            loop.create_task(
                self.quarantine_orchestrator.quarantine(alert))
        await msg.ack()
