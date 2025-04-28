from pydantic import Field
from pydantic_settings import BaseSettings

class EMQXSettings(BaseSettings):
    """Settings specific to EMQX protocol quarantine."""
    base_url: str = Field(default="http://localhost:18083/api/v5", description="EMQX API base URL")
    api_key: str = Field(min_length=8, description="EMQX API key")
    api_secret: str = Field(min_length=8, description="EMQX API secret")