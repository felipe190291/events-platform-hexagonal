"""Attendee domain entity. User-event registration tracking."""

from datetime import datetime
from pydantic import BaseModel, Field
from app.domain.enums import AttendeeStatus


class AttendeeEntity(BaseModel):
    """Core attendee entity (user-event registration)."""
    id: int | None = None
    user_id: int
    event_id: int
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    status: AttendeeStatus = AttendeeStatus.REGISTERED
