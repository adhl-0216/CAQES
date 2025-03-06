from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.networks import IPvAnyAddress


class Alert(BaseModel):
    source_ip: IPvAnyAddress
    destination_ip: IPvAnyAddress
    priority: str
    timestamp: datetime = Field(default_factory=datetime.now)
    classification: str
    raw: str | None = None
