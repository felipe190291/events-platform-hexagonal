"""Attendee service orchestrating registrations."""

from app.domain.entities.attendee import AttendeeEntity
from app.domain.enums import AttendeeStatus, EventStatus
from app.domain.exceptions import (
    CapacityExceededException,
    DuplicateEntityException,
    EntityNotFoundException,
    InvalidOperationException,
)
from app.domain.ports.attendee_repository import AttendeeRepositoryPort
from app.domain.ports.event_repository import EventRepositoryPort


class AttendeeService:
    """Orchestrates attendee registration business operations."""

    def __init__(self, attendee_repo: AttendeeRepositoryPort, event_repo: EventRepositoryPort):
        self._attendee_repo = attendee_repo
        self._event_repo = event_repo

    def register_to_event(self, user_id: int, event_id: int) -> AttendeeEntity:
        """Register a user to an event."""
        event = self._event_repo.get_by_id(event_id)
        if not event:
            raise EntityNotFoundException("Event", event_id)

        if event.status != EventStatus.PUBLISHED:
            raise InvalidOperationException("Can only register to published events")

        existing = self._attendee_repo.get_by_user_and_event(user_id, event_id)
        if existing and existing.status == AttendeeStatus.REGISTERED:
            raise DuplicateEntityException("Attendee", "user_id+event_id", f"{user_id}+{event_id}")

        if self._attendee_repo.count_by_event(event_id) >= event.capacity:
            raise CapacityExceededException("Event")

        if existing and existing.status == AttendeeStatus.CANCELLED:
            existing.status = AttendeeStatus.REGISTERED
            return self._attendee_repo.update(existing)

        return self._attendee_repo.create(AttendeeEntity(user_id=user_id, event_id=event_id))

    def unregister_from_event(self, user_id: int, event_id: int) -> AttendeeEntity:
        """Cancel a user's registration."""
        attendee = self._attendee_repo.get_by_user_and_event(user_id, event_id)
        if not attendee or attendee.status == AttendeeStatus.CANCELLED:
            raise EntityNotFoundException("Registration", f"user={user_id}, event={event_id}")

        attendee.status = AttendeeStatus.CANCELLED
        return self._attendee_repo.update(attendee)

    def get_user_events(self, user_id: int) -> list[int]:
        """Get all event IDs a user is actively registered to."""
        return self._attendee_repo.get_events_by_user(user_id)

    def get_event_attendees(self, event_id: int, page: int = 1, size: int = 100) -> tuple[list[AttendeeEntity], int]:
        """Get all attendees for an event."""
        skip = (page - 1) * size
        return self._attendee_repo.get_by_event(event_id, skip=skip, limit=size)
