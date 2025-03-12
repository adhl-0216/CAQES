import asyncio

from caqes_core.worker import Worker
from settings.caqes_settings import CaqesSettings


class CAQES:
    def __init__(self, settings: CaqesSettings = None):
        self.settings = settings or CaqesSettings()

    async def start(self):
        num_workers = self.settings.num_workers
        workers = [Worker() for _ in range(num_workers)]
        tasks = [worker.run() for worker in workers]
        await asyncio.gather(*tasks)


def main():
    app = CAQES()
    asyncio.run(app.start())


if __name__ == "__main__":
    main()
