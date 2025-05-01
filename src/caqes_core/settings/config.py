import logging
import yaml
from pathlib import Path
from caqes_core.settings import WorkerSettings, OrchestratorSettings

logger = logging.getLogger(__name__)

class ConfigManager:
    _instance = None

    def __new__(cls, config_path: str = "caqes.conf"):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize(config_path)
        return cls._instance

    def _initialize(self, config_path: str):
        """Load configuration and initialize settings objects."""
        try:
            config_path = Path(config_path)
            if not config_path.exists():
                logger.warning(f"Configuration file {config_path} not found, using defaults")
                self._num_workers = 1
                self._worker_settings = WorkerSettings()
                self._orchestrator_settings = OrchestratorSettings()
                return

            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f) or {}

            self._num_workers = config_data.get("num_workers", 1)
            self._worker_settings = WorkerSettings(config_dict=config_data.get("worker", {}))
            self._orchestrator_settings = OrchestratorSettings(config_dict=config_data.get("quarantine", {}))
            logger.info(f"Loaded configuration from {config_path}")

        except Exception as e:
            logger.error(f"Error initializing ConfigManager: {e}")
            self._num_workers = 1
            self._worker_settings = WorkerSettings()
            self._orchestrator_settings = OrchestratorSettings()

    @property
    def num_workers(self) -> int:
        return self._num_workers

    @property
    def worker_settings(self) -> WorkerSettings:
        return self._worker_settings

    @property
    def orchestrator_settings(self) -> OrchestratorSettings:
        return self._orchestrator_settings