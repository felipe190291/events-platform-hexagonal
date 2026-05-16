"""Session repository port definition."""

from abc import ABC, abstractmethod
from datetime import datetime
from app.domain.entities.session import SessionEntity


class SessionRepositoryPort(ABC):
    """Abstract port for session data access operations."""

    @abstractmethod
    def create(self, session: SessionEntity) -> SessionEntity:
        """Persist a new session and return it with the generated ID."""
        ...

    @abstractmethod
    def get_by_id(self, session_id: int) -> SessionEntity | None:
        """Retrieve a session by its unique identifier."""
        ...

    @abstractmethod
    def get_by_event(self, event_id: int) -> list[SessionEntity]:
        """Retrieve all sessions belonging to a specific event."""
        ...

    @abstractmethod
    def update(self, session: SessionEntity) -> SessionEntity:
        """Update an existing session's data."""
        ...

    @abstractmethod
    def delete(self, session_id: int) -> bool:
        """Delete a session by its ID."""
        ...

    @abstractmethod
    def check_time_overlap(
        self, event_id: int, start_time: datetime, end_time: datetime, exclude_id: int | None = None
    ) -> bool:
        """Check if a time range overlaps with existing sessions in an event."""
        ...
