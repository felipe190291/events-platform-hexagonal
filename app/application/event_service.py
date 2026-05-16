"""Event service orchestrating event CRUD and search."""

from app.domain.entities.event import EventEntity
from app.domain.enums import EventStatus, UserRole
from app.domain.exceptions import (
    AuthorizationException,
    EntityNotFoundException,
    InvalidOperationException,
)
from app.domain.ports.event_repository import EventRepositoryPort
from app.domain.ports.cache_port import CachePort


class EventService:
    """Orchestrates event-related business operations."""

    def __init__(self, event_repo: EventRepositoryPort, cache: CachePort):
        self._event_repo = event_repo
        self._cache = cache

    def create_event(self, event_data: dict, organizer_id: int) -> EventEntity:
        """Create a new event with business validations."""
        if event_data["end_date"] <= event_data["start_date"]:
            raise InvalidOperationException("End date must be after start date")

        event = EventEntity(**event_data, organizer_id=organizer_id)
        created = self._event_repo.create(event)
        self._cache.delete_pattern("events:*")
        return created

    def get_event(self, event_id: int) -> EventEntity:
        """Retrieve a single event by its ID."""
        event = self._event_repo.get_by_id(event_id)
        if not event:
            raise EntityNotFoundException("Event", event_id)
        return event

    def search_events(
        self,
        query: str | None = None,
        status: EventStatus | None = None,
        organizer_id: int | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[EventEntity], int]:
        """Search events with optional filters and pagination."""
        skip = (page - 1) * size
        return self._event_repo.search(
            query=query, 
            status=status, 
            organizer_id=organizer_id, 
            skip=skip, 
            limit=size
        )

    def update_event(
        self, event_id: int, event_data: dict, user_id: int, user_role: UserRole
    ) -> EventEntity:
        """Update an existing event with authorization and validation."""
        event = self._event_repo.get_by_id(event_id)
        if not event:
            raise EntityNotFoundException("Event", event_id)

        if user_role != UserRole.ADMIN and event.organizer_id != user_id:
            raise AuthorizationException("Only the organizer or admin can update this event")

        if event.status in (EventStatus.COMPLETED, EventStatus.CANCELLED):
            raise InvalidOperationException(f"Cannot update an event with status '{event.status.value}'")

        if "end_date" in event_data and "start_date" in event_data:
            if event_data["end_date"] <= event_data["start_date"]:
                raise InvalidOperationException("End date must be after start date")

        for key, value in event_data.items():
            setattr(event, key, value)

        updated = self._event_repo.update(event)
        self._cache.delete_pattern("events:*")
        return updated

    def delete_event(self, event_id: int, user_id: int, user_role: UserRole) -> bool:
        """Delete an event (ADMIN only)."""
        event = self._event_repo.get_by_id(event_id)
        if not event:
            raise EntityNotFoundException("Event", event_id)

        if user_role != UserRole.ADMIN:
            raise AuthorizationException("Only admins can delete events")

        result = self._event_repo.delete(event_id)
        self._cache.delete_pattern("events:*")
        return result
