"""Event domain entity. No framework or database dependencies."""

from datetime import datetime
from pydantic import BaseModel, Field
from app.domain.enums import EventStatus


class EventEntity(BaseModel):
    """Core event entity with all business attributes."""
    id: int | None = None
    title: str
    description: str
    location: str
    start_date: datetime
    end_date: datetime
    capacity: int = Field(gt=0)
    status: EventStatus = EventStatus.DRAFT
    image_url: str | None = None
    organizer_id: int | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    attendee_count: int = 0
