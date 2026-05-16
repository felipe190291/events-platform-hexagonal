"""Event management API endpoints."""

import math
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_event_service, get_current_user, get_current_organizer_or_admin
from app.api.schemas.event import CreateEventRequest, EventListResponse, EventResponse, UpdateEventRequest
from app.application.event_service import EventService
from app.domain.entities.user import UserEntity
from app.domain.enums import EventStatus
from app.domain.exceptions import AuthorizationException, EntityNotFoundException, InvalidOperationException

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=EventListResponse)
def list_events(
    event_service: Annotated[EventService, Depends(get_event_service)],
    query: str | None = Query(default=None),
    status_filter: EventStatus | None = Query(default=None, alias="status"),
    organizer_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
):
    """List all events with optional search and pagination."""
    events, total = event_service.search_events(
        query=query, 
        status=status_filter, 
        organizer_id=organizer_id, 
        page=page, 
        size=size
    )
    pages = math.ceil(total / size) if total > 0 else 0
    return EventListResponse(events=[EventResponse.model_validate(e.model_dump()) for e in events], total=total, page=page, size=size, pages=pages)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, event_service: Annotated[EventService, Depends(get_event_service)]):
    """Retrieve a single event by its ID."""
    try:
        event = event_service.get_event(event_id)
        return EventResponse.model_validate(event.model_dump())
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(request: CreateEventRequest, event_service: Annotated[EventService, Depends(get_event_service)], current_user: Annotated[UserEntity, Depends(get_current_organizer_or_admin)]):
    """Create a new event."""
    try:
        # If admin provides an organizer_id, use it. Otherwise use current user.
        target_organizer_id = current_user.id
        from app.domain.enums import UserRole
        if current_user.role == UserRole.ADMIN and request.organizer_id:
            target_organizer_id = request.organizer_id
            
        event_dict = request.model_dump(exclude={"organizer_id"})
        event = event_service.create_event(event_data=event_dict, organizer_id=target_organizer_id)
        return EventResponse.model_validate(event.model_dump())
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.put("/{event_id}", response_model=EventResponse)
@router.patch("/{event_id}", response_model=EventResponse)
def update_event(event_id: int, request: UpdateEventRequest, event_service: Annotated[EventService, Depends(get_event_service)], current_user: Annotated[UserEntity, Depends(get_current_user)]):
    """Update an existing event."""
    try:
        event = event_service.update_event(event_id=event_id, event_data=request.model_dump(exclude_unset=True), user_id=current_user.id, user_role=current_user.role)
        return EventResponse.model_validate(event.model_dump())
    except (EntityNotFoundException, AuthorizationException, InvalidOperationException) as e:
        status_code = status.HTTP_404_NOT_FOUND if isinstance(e, EntityNotFoundException) else status.HTTP_403_FORBIDDEN if isinstance(e, AuthorizationException) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=e.message)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, event_service: Annotated[EventService, Depends(get_event_service)], current_user: Annotated[UserEntity, Depends(get_current_user)]):
    """Delete an event (ADMIN only)."""
    try:
        event_service.delete_event(event_id=event_id, user_id=current_user.id, user_role=current_user.role)
    except (EntityNotFoundException, AuthorizationException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND if isinstance(e, EntityNotFoundException) else status.HTTP_403_FORBIDDEN, detail=e.message)
