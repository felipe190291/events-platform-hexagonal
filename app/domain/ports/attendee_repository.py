"""Attendee repository port definition."""

from abc import ABC, abstractmethod
from app.domain.entities.attendee import AttendeeEntity


class AttendeeRepositoryPort(ABC):
    """Abstract port for attendee data access operations."""

    @abstractmethod
    def create(self, attendee: AttendeeEntity) -> AttendeeEntity:
        """Register a user to an event."""
        ...

    @abstractmethod
    def get_by_user_and_event(self, user_id: int, event_id: int) -> AttendeeEntity | None:
        """Find a registration for a specific user and event combination."""
        ...

    @abstractmethod
    def get_by_event(self, event_id: int, skip: int = 0, limit: int = 100) -> tuple[list[AttendeeEntity], int]:
        """Retrieve all attendees registered for a specific event."""
        ...

    @abstractmethod
    def get_events_by_user(self, user_id: int) -> list[int]:
        """Retrieve all event IDs a user is registered to."""
        ...

    @abstractmethod
    def update(self, attendee: AttendeeEntity) -> AttendeeEntity:
        """Update an attendee registration (e.g., cancel)."""
        ...

    @abstractmethod
    def count_by_event(self, event_id: int) -> int:
        """Count the number of active registrations for an event."""
        ...
