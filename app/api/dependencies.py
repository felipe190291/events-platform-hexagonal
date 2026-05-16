"""API dependency injection wiring hexagonal ports to adapters."""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from app.domain.entities.user import UserEntity
from app.domain.enums import UserRole
from app.infrastructure.database.connection import get_session
from app.infrastructure.database.repositories.user_repository import SQLModelUserRepository
from app.infrastructure.database.repositories.event_repository import SQLModelEventRepository
from app.infrastructure.database.repositories.session_repository import SQLModelSessionRepository
from app.infrastructure.database.repositories.attendee_repository import SQLModelAttendeeRepository
from app.infrastructure.cache.memory_cache import InMemoryCacheAdapter
from app.infrastructure.security.jwt_handler import decode_access_token
from app.application.auth_service import AuthService
from app.application.event_service import EventService
from app.application.session_service import SessionService
from app.application.attendee_service import AttendeeService

security = HTTPBearer()
_cache = InMemoryCacheAdapter()


def get_cache():
    return _cache


def get_user_repo(session: Annotated[Session, Depends(get_session)]) -> SQLModelUserRepository:
    return SQLModelUserRepository(session)


def get_event_repo(session: Annotated[Session, Depends(get_session)]) -> SQLModelEventRepository:
    return SQLModelEventRepository(session)


def get_session_repo(session: Annotated[Session, Depends(get_session)]) -> SQLModelSessionRepository:
    return SQLModelSessionRepository(session)


def get_attendee_repo(session: Annotated[Session, Depends(get_session)]) -> SQLModelAttendeeRepository:
    return SQLModelAttendeeRepository(session)


def get_auth_service(user_repo: Annotated[SQLModelUserRepository, Depends(get_user_repo)]) -> AuthService:
    return AuthService(user_repo)


def get_event_service(
    event_repo: Annotated[SQLModelEventRepository, Depends(get_event_repo)],
    cache: Annotated[InMemoryCacheAdapter, Depends(get_cache)],
) -> EventService:
    return EventService(event_repo, cache)


def get_session_service(
    session_repo: Annotated[SQLModelSessionRepository, Depends(get_session_repo)],
    event_repo: Annotated[SQLModelEventRepository, Depends(get_event_repo)],
) -> SessionService:
    return SessionService(session_repo, event_repo)


def get_attendee_service(
    attendee_repo: Annotated[SQLModelAttendeeRepository, Depends(get_attendee_repo)],
    event_repo: Annotated[SQLModelEventRepository, Depends(get_event_repo)],
) -> AttendeeService:
    return AttendeeService(attendee_repo, event_repo)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_repo: Annotated[SQLModelUserRepository, Depends(get_user_repo)],
) -> UserEntity:
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = user_repo.get_by_id(int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def get_current_admin(current_user: Annotated[UserEntity, Depends(get_current_user)]) -> UserEntity:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def get_current_organizer_or_admin(current_user: Annotated[UserEntity, Depends(get_current_user)]) -> UserEntity:
    if current_user.role not in (UserRole.ADMIN, UserRole.ORGANIZER):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organizer or admin access required")
    return current_user
