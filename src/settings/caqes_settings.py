import yaml
from pydantic_settings import BaseSettings


class CaqesSettings(BaseSettings):
    num_workers: int = 3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open("/workspaces/caqes.conf", "r") as f:
            config = yaml.safe_load(f)
            if "num_workers" in config:
                self.num_workers = config["num_workers"]
