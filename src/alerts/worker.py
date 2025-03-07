from uuid import uuid4
import nats
import asyncio
import json

from nats.aio.client import Client, Msg
from nats.js import JetStreamContext
from nats.js.errors import NotFoundError
from nats.js.api import StreamConfig

from config.settings import settings
from models import Job, Alert

ALERTS_STREAM = "ALERTS"
JOBS_STREAM = "JOBS"


class Worker:
    def __init__(self):
        self.nc: Client | None = None
        self.js: JetStreamContext | None = None
        self.worker_id = uuid4()
        self.config = settings

        self.connect()
        self.start()
        self.close()

    async def _try_connect(self) -> tuple[Client, JetStreamContext]:
        nc = await nats.connect(settings.url)
        js = await nc.jetstream()
        return nc, js

    async def connect(self):
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                self.nc, self.js = await self._try_connect()
                return
            except Exception as e:
                last_error = e
                if attempt < settings.max_retries - 1:
                    await asyncio.sleep(settings.retry_delay * (2 ** attempt))

        raise ConnectionError(
            f"Failed to connect after {self.config.max_retries} attempts. Last error: {last_error}")

    async def close(self):
        if self.nc:
            try:
                await self.nc.close()
            except Exception as e:
                raise e

    async def _ensure_stream(self) -> None:
        """Creates the alerts and jobs streams if they don't exist"""
        try:
            await self.js.stream_info(ALERTS_STREAM)
        except NotFoundError:
            config = StreamConfig(
                name=ALERTS_STREAM,
                subjects=[ALERTS_STREAM],
                retention="workqueue",
                max_msgs=10_000,
            )
            await self.js.add_stream(config)

    async def _parse_alert(self, msg: Msg):
        data = json.loads(msg.data.decode())
        alert = Alert(**data)
        if alert.priority in {"1", "2"}:
            # TODO: placeholder for quarantine logic
            asyncio.create_task(print(alert))
        await msg.ack()

    async def start(self) -> None:
        """Start the alert listener"""
        if not self.js:
            try:
                await self.connect()
            except Exception as e:
                raise e

        await self._ensure_stream()
        sub = await self.js.subscribe(
            f"{ALERTS_STREAM}.>",
        )

        async for msg in sub.messages:
            try:
                self._parse_alert(msg)
            except Exception as e:
                print(f"Worker {self.worker_id} error: {e}")
                await msg.nak()
