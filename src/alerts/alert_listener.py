import nats


class AlertListener:
    def __init__(self):
        self.nc = None
        self.js = None

    async def connect(self):
        self.nc = await nats.connect("nats://nats:4222")

    async def close(self):
        if self.nc:
            await self.nc.close()
