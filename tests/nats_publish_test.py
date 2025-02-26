import asyncio
from nats.aio.client import Client as NATS

async def main():
    nc = NATS()
    await nc.connect("nats://nats:4222")

    await nc.publish("test", b'Hello, NATS!')
    await nc.flush()
    await nc.close()

if __name__ == '__main__':
    asyncio.run(main())