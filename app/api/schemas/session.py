"""Session request/response schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    speaker_name: str = Field(..., min_length=2)
    start_time: datetime
    end_time: datetime


class UpdateSessionRequest(BaseModel):
    title: str | None = Field(default=None, min_length=3)
    description: str | None = Field(default=None, min_length=10)
    speaker_name: str | None = Field(default=None, min_length=2)
    start_time: datetime | None = None
    end_time: datetime | None = None


class SessionResponse(BaseModel):
    id: int
    title: str
    description: str
    speaker_name: str
    start_time: datetime
    end_time: datetime
    event_id: int

    model_config = {"from_attributes": True}
