from datetime import datetime
from typing import Optional
from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    alert_data: str = Field(description="Raw log data to be parsed")
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
