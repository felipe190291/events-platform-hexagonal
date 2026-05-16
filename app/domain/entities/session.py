"""Session domain entity. A talk/workshop within an event."""

from datetime import datetime
from pydantic import BaseModel


class SessionEntity(BaseModel):
    """Core session entity within an event."""
    id: int | None = None
    title: str
    description: str
    speaker_name: str
    start_time: datetime
    end_time: datetime
    event_id: int | None = None
