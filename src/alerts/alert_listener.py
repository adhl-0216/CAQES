import nats
from nats.aio.client import Client
from nats.js import JetStreamContext
from config.settings import settings
import asyncio


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
