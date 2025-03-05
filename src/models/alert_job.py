from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AlertJob(BaseModel):
    job_id: str
    alert_data: dict
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
