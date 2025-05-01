from datetime import datetime
import logging
from pydantic import BaseModel, Field, field_validator
from pydantic.networks import IPvAnyAddress
from uuid import uuid4


class Alert(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    source_ip: IPvAnyAddress
    source_port: int
    destination_ip: IPvAnyAddress
    destination_port: int
    priority: str = Field(default='1')
    timestamp: datetime | None = Field(default_factory=datetime.now)
    classification: str | None = Field(default="Others")
    raw: str

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value):
        """
        Handle None or invalid timestamp values by returning the current time.
        Optionally parse string timestamps if needed.
        """
        if value is None:
            return datetime.now()
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                logging.getLogger().warning(
                    f"Invalid timestamp format: {value}, using current time")
                return datetime.now()
        return value

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, value):
        """
        Handle None by returning 'Others'.
        """
        if value is None:
            return "Others"
