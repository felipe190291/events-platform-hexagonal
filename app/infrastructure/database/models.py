"""SQLModel ORM models for database tables."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, String
from app.domain.enums import UserRole, EventStatus, AttendeeStatus


class UserModel(SQLModel, table=True):
    """Database table model for users."""
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    hashed_password: str
    full_name: str
    role: UserRole = Field(default=UserRole.ATTENDEE)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    organized_events: List["EventModel"] = Relationship(
        back_populates="organizer",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    attendee_records: List["AttendeeModel"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class EventModel(SQLModel, table=True):
    """Database table model for events."""
    __tablename__ = "events"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str
    location: str
    start_date: datetime
    end_date: datetime
    capacity: int = Field(gt=0)
    status: EventStatus = Field(default=EventStatus.DRAFT)
    image_url: str | None = Field(default=None)
    organizer_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    organizer: Optional[UserModel] = Relationship(back_populates="organized_events")
    sessions: List["SessionModel"] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    attendees: List["AttendeeModel"] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class SessionModel(SQLModel, table=True):
    """Database table model for event sessions."""
    __tablename__ = "sessions"

    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str
    speaker_name: str
    start_time: datetime
    end_time: datetime
    event_id: int = Field(foreign_key="events.id", ondelete="CASCADE")

    event: Optional[EventModel] = Relationship(back_populates="sessions")


class AttendeeModel(SQLModel, table=True):
    """Database table model for event attendee registrations."""
    __tablename__ = "attendees"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    event_id: int = Field(foreign_key="events.id", ondelete="CASCADE")
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    status: AttendeeStatus = Field(default=AttendeeStatus.REGISTERED)

    user: Optional[UserModel] = Relationship(back_populates="attendee_records")
    event: Optional[EventModel] = Relationship(back_populates="attendees")
