from pydantic_settings import BaseSettings


class CaqesSettings(BaseSettings):
    num_workers: int = 3
