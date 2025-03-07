from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from pydantic.networks import IPvAnyAddress


class Alert(BaseModel):
    source_ip: IPvAnyAddress
    destination_ip: IPvAnyAddress
    priority: int
    timestamp: datetime = Field(default_factory=datetime.now)
    classification: str
    raw: str | None = None
