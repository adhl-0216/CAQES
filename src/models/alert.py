from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class Alert(BaseModel):
    ip_address: str
    hostname: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: str = Field(default="medium")
    description: Optional[str] = None
    alert_type: str = Field(default="ids")
