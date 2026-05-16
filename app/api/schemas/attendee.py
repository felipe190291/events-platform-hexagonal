"""Attendee request/response schemas."""

from datetime import datetime
from pydantic import BaseModel


class AttendeeResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    registered_at: datetime
    status: str

    model_config = {"from_attributes": True}


class AttendeeListResponse(BaseModel):
    attendees: list[AttendeeResponse]
    total: int
