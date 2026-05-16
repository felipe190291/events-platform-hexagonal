"""Event request/response schemas."""

from datetime import datetime
from pydantic import BaseModel, Field
from app.domain.enums import EventStatus


class CreateEventRequest(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    location: str = Field(..., min_length=3)
    start_date: datetime
    end_date: datetime
    capacity: int = Field(..., gt=0)
    status: EventStatus = Field(default=EventStatus.DRAFT)
    image_url: str | None = Field(default=None)
    organizer_id: int | None = Field(default=None)


class UpdateEventRequest(BaseModel):
    title: str | None = Field(default=None, min_length=3)
    description: str | None = Field(default=None, min_length=10)
    location: str | None = Field(default=None, min_length=3)
    start_date: datetime | None = None
    end_date: datetime | None = None
    capacity: int | None = Field(default=None, gt=0)
    status: EventStatus | None = None
    image_url: str | None = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    start_date: datetime
    end_date: datetime
    capacity: int
    status: EventStatus
    image_url: str | None
    organizer_id: int
    created_at: datetime
    attendee_count: int = 0

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    events: list[EventResponse]
    total: int
    page: int
    size: int
    pages: int
