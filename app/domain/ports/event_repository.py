"""Event repository port definition."""

from abc import ABC, abstractmethod
from app.domain.entities.event import EventEntity
from app.domain.enums import EventStatus


class EventRepositoryPort(ABC):
    """Abstract port for event data access operations."""

    @abstractmethod
    def create(self, event: EventEntity) -> EventEntity:
        """Persist a new event and return it with the generated ID."""
        ...

    @abstractmethod
    def get_by_id(self, event_id: int) -> EventEntity | None:
        """Retrieve an event by its unique identifier."""
        ...

    @abstractmethod
    def search(
        self,
        query: str | None = None,
        status: EventStatus | None = None,
        organizer_id: int | None = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[EventEntity], int]:
        """Search events with optional filters and pagination."""
        ...

    @abstractmethod
    def get_by_organizer(self, organizer_id: int) -> list[EventEntity]:
        """Retrieve all events created by a specific organizer."""
        ...

    @abstractmethod
    def update(self, event: EventEntity) -> EventEntity:
        """Update an existing event's data."""
        ...

    @abstractmethod
    def delete(self, event_id: int) -> bool:
        """Delete an event by its ID."""
        ...
