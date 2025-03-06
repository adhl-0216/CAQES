import nats
from nats.aio.client import Client
from nats.js import JetStreamContext
from config.settings import settings
from nats.js.errors import NotFoundError
import asyncio
from nats.js.api import StreamConfig

ALERTS_STREAM = "ALERTS"
JOBS_STREAM = "JOBS"


class AlertListener:
    def __init__(self):
        self.nc: Client | None = None
        self.js: JetStreamContext | None = None
        self.config = settings

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

    async def _ensure_streams(self) -> None:
        """Creates the alerts and jobs streams if they don't exist"""
        streams = {
            ALERTS_STREAM: f"{ALERTS_STREAM}.>",
            JOBS_STREAM: f"{JOBS_STREAM}.>"
        }

        for stream, subject in streams.items():
            try:
                await self.js.stream_info(stream)
            except NotFoundError:
                config = StreamConfig(
                    name=stream,
                    subjects=[subject],
                    retention="workqueue",
                    max_msgs=10_000,
                )
                await self.js.add_stream(config)

    async def _handle_alert_message(self, msg: nats.aio.msg.Msg) -> None:
        pass

    async def start(self) -> None:
        """Start the alert listener"""
        if not self.js:
            try:
                await self.connect()
            except Exception as e:
                raise e

        await self._ensure_streams()
        await self.js.subscribe(
            f"{ALERTS_STREAM}.>",
            cb=self._handle_alert_message
        )
