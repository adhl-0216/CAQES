import asyncio
import logging

from caqes_core.worker import Worker
from quarantine.quarantine_orchestrator import QuarantineOrchestrator
from loggers.audit_logger import init_logger
from settings.config import ConfigManager


class CAQES:
    @classmethod
    async def start(cls, config_path: str = "caqes.conf"):
        init_logger()
        logger = logging.getLogger("caqes")
        config = ConfigManager(config_path=config_path)
        orchestrator = QuarantineOrchestrator(settings=config.orchestrator_settings)

        logger.info(f"Starting CAQES with {config.num_workers} workers")
        workers = [
            Worker(settings=config.worker_settings, orchestrator=orchestrator)
            for _ in range(config.num_workers)
        ]
        tasks = [worker.run() for worker in workers]
        await asyncio.gather(*tasks)


def main():
    asyncio.run(CAQES.start())


if __name__ == "__main__":
    main()
