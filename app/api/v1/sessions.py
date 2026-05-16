"""Session management API endpoints."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_session_service, get_current_user, get_current_organizer_or_admin
from app.api.schemas.session import CreateSessionRequest, SessionResponse, UpdateSessionRequest
from app.application.session_service import SessionService
from app.domain.entities.user import UserEntity
from app.domain.exceptions import AuthorizationException, EntityNotFoundException, InvalidOperationException

router = APIRouter(tags=["Sessions"])


@router.get("/events/{event_id}/sessions", response_model=list[SessionResponse])
def list_event_sessions(event_id: int, session_service: Annotated[SessionService, Depends(get_session_service)]):
    """List all sessions for a specific event."""
    try:
        sessions = session_service.get_event_sessions(event_id)
        return [SessionResponse.model_validate(s.model_dump()) for s in sessions]
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/events/{event_id}/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(event_id: int, request: CreateSessionRequest, session_service: Annotated[SessionService, Depends(get_session_service)], current_user: Annotated[UserEntity, Depends(get_current_organizer_or_admin)]):
    """Create a new session within an event."""
    try:
        session = session_service.create_session(session_data=request.model_dump(), event_id=event_id, user_id=current_user.id, user_role=current_user.role)
        return SessionResponse.model_validate(session.model_dump())
    except (EntityNotFoundException, AuthorizationException, InvalidOperationException) as e:
        status_code = status.HTTP_404_NOT_FOUND if isinstance(e, EntityNotFoundException) else status.HTTP_403_FORBIDDEN if isinstance(e, AuthorizationException) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=e.message)


@router.put("/sessions/{session_id}", response_model=SessionResponse)
def update_session(session_id: int, request: UpdateSessionRequest, session_service: Annotated[SessionService, Depends(get_session_service)], current_user: Annotated[UserEntity, Depends(get_current_user)]):
    """Update an existing session."""
    try:
        session = session_service.update_session(session_id=session_id, session_data=request.model_dump(exclude_unset=True), user_id=current_user.id, user_role=current_user.role)
        return SessionResponse.model_validate(session.model_dump())
    except (EntityNotFoundException, AuthorizationException, InvalidOperationException) as e:
        status_code = status.HTTP_404_NOT_FOUND if isinstance(e, EntityNotFoundException) else status.HTTP_403_FORBIDDEN if isinstance(e, AuthorizationException) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=e.message)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, session_service: Annotated[SessionService, Depends(get_session_service)], current_user: Annotated[UserEntity, Depends(get_current_user)]):
    """Delete a session from an event."""
    try:
        session_service.delete_session(session_id=session_id, user_id=current_user.id, user_role=current_user.role)
    except (EntityNotFoundException, AuthorizationException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if isinstance(e, EntityNotFoundException) else status.HTTP_403_FORBIDDEN, detail=e.message)
