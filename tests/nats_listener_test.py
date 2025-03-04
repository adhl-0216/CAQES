import asyncio
from nats.aio.client import Client as NATS

async def message_handler(msg):
    subject = msg.subject
    data = msg.data.decode()
    print(f"Received a message on '{subject}': {data}")

async def main():
    nc = NATS()
    await nc.connect("nats://nats:4222")

    # Subscribe to the subject 'test'
    await nc.subscribe("test", cb=message_handler)

    # Keep the listener running
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())