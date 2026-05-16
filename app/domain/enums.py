"""Domain layer enumerations. Framework-agnostic business enums."""

from enum import Enum


class UserRole(str, Enum):
    """User authorization roles: ADMIN, ORGANIZER, ATTENDEE."""
    ADMIN = "admin"
    ORGANIZER = "organizer"
    ATTENDEE = "attendee"


class EventStatus(str, Enum):
    """Event lifecycle: DRAFT -> PUBLISHED -> IN_PROGRESS -> COMPLETED. Can be CANCELLED."""
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AttendeeStatus(str, Enum):
    """Attendee registration status."""
    REGISTERED = "registered"
    CANCELLED = "cancelled"
