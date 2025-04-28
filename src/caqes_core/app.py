import asyncio
import logging
import os

from caqes_core.worker import Worker
from caqes_core.quarantine.quarantine_orchestrator import QuarantineOrchestrator
from caqes_core.loggers.audit_logger import init_logger
from caqes_core.settings.config import ConfigManager


class CAQES:
    @classmethod
    async def start(cls):
        config_path = os.getenv("CONFIG_PATH", "caqes.conf")
        init_logger()
        logger = logging.getLogger("caqes")
        logger.info(f"Using config from {config_path}")
        
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
