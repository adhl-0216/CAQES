import asyncio
import json

from settings.worker_settings import WorkerSettings

from models import Alert

from mq.client_factory import ClientFactory
from mq.mq_client import MQClient
from mq.message import Message

from quarantine.quarantine_orchestrator import QuarantineOrchestrator


class Worker:
    def __init__(self, settings: WorkerSettings | None = None):
        self.mq: MQClient | None = None
        self.settings = settings or WorkerSettings()
        self.quarantine_orchestrator = QuarantineOrchestrator(settings)

    async def run(self) -> None:
        try:
            await self._ensure_connected()

            await self.mq.subscribe("alerts", self._handle_alert)

            # Keep the worker running
            while True:
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Worker error: {e}")
        finally:
            if self.mq:
                await self.mq.close()

    async def _ensure_connected(self) -> None:
        if not self.mq:
            self.mq = ClientFactory.create(self.settings.mq_client_type)
        if not await self.mq.is_connected():
            try:
                await self.mq.connect()
            except Exception as e:
                raise e

    async def _handle_alert(self, msg: Message) -> None:
        if not msg.data:
            await msg.nak()
            raise ValueError("Message data is empty")

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
