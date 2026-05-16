"""Session service orchestrating event sessions."""

from app.domain.entities.session import SessionEntity
from app.domain.enums import UserRole
from app.domain.exceptions import (
    AuthorizationException,
    EntityNotFoundException,
    InvalidOperationException,
)
from app.domain.ports.session_repository import SessionRepositoryPort
from app.domain.ports.event_repository import EventRepositoryPort


class SessionService:
    """Orchestrates session-related business operations."""

    def __init__(self, session_repo: SessionRepositoryPort, event_repo: EventRepositoryPort):
        self._session_repo = session_repo
        self._event_repo = event_repo

    def create_session(self, session_data: dict, event_id: int, user_id: int, user_role: UserRole) -> SessionEntity:
        """Create a new session within an event."""
        event = self._event_repo.get_by_id(event_id)
        if not event:
            raise EntityNotFoundException("Event", event_id)

        if user_role != UserRole.ADMIN and event.organizer_id != user_id:
            raise AuthorizationException("Only the organizer or admin can add sessions")

        if session_data["end_time"] <= session_data["start_time"]:
            raise InvalidOperationException("Session end time must be after start time")

        if self._session_repo.check_time_overlap(event_id, session_data["start_time"], session_data["end_time"]):
            raise InvalidOperationException("Session time overlaps with an existing session")

        session = SessionEntity(**session_data, event_id=event_id)
        return self._session_repo.create(session)

    def get_event_sessions(self, event_id: int) -> list[SessionEntity]:
        """Retrieve all sessions for a given event."""
        if not self._event_repo.get_by_id(event_id):
            raise EntityNotFoundException("Event", event_id)
        return self._session_repo.get_by_event(event_id)

    def update_session(self, session_id: int, session_data: dict, user_id: int, user_role: UserRole) -> SessionEntity:
        """Update an existing session with validation."""
        session = self._session_repo.get_by_id(session_id)
        if not session:
            raise EntityNotFoundException("Session", session_id)

        event = self._event_repo.get_by_id(session.event_id)
        if user_role != UserRole.ADMIN and event.organizer_id != user_id:
            raise AuthorizationException("Only the organizer or admin can update sessions")

        start = session_data.get("start_time", session.start_time)
        end = session_data.get("end_time", session.end_time)
        if end <= start:
            raise InvalidOperationException("Session end time must be after start time")

        if self._session_repo.check_time_overlap(session.event_id, start, end, exclude_id=session_id):
            raise InvalidOperationException("Session time overlaps with an existing session")

        for key, value in session_data.items():
            setattr(session, key, value)
        return self._session_repo.update(session)

    def delete_session(self, session_id: int, user_id: int, user_role: UserRole) -> bool:
        """Delete a session from an event."""
        session = self._session_repo.get_by_id(session_id)
        if not session:
            raise EntityNotFoundException("Session", session_id)

        event = self._event_repo.get_by_id(session.event_id)
        if user_role != UserRole.ADMIN and event.organizer_id != user_id:
            raise AuthorizationException("Only the organizer or admin can delete sessions")

        return self._session_repo.delete(session_id)
