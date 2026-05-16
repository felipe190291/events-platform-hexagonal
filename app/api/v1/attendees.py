"""Attendee registration API endpoints."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_attendee_service, get_event_service, get_current_user, get_current_organizer_or_admin
from app.api.schemas.attendee import AttendeeListResponse, AttendeeResponse
from app.api.schemas.event import EventResponse
from app.application.attendee_service import AttendeeService
from app.application.event_service import EventService
from app.domain.entities.user import UserEntity
from app.domain.exceptions import CapacityExceededException, DuplicateEntityException, EntityNotFoundException, InvalidOperationException

router = APIRouter(tags=["Attendees"])


@router.post("/events/{event_id}/register", response_model=AttendeeResponse, status_code=status.HTTP_201_CREATED)
def register_to_event(event_id: int, attendee_service: Annotated[AttendeeService, Depends(get_attendee_service)], current_user: Annotated[UserEntity, Depends(get_current_user)]):
    """Register the current user to an event."""
    try:
        attendee = attendee_service.register_to_event(user_id=current_user.id, event_id=event_id)
        return AttendeeResponse.model_validate(attendee.model_dump())
    except (EntityNotFoundException, InvalidOperationException, DuplicateEntityException, CapacityExceededException) as e:
        status_code = status.HTTP_404_NOT_FOUND if isinstance(e, EntityNotFoundException) else status.HTTP_409_CONFLICT if isinstance(e, DuplicateEntityException) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=e.message)


@router.delete("/events/{event_id}/unregister")
def unregister_from_event(event_id: int, attendee_service: Annotated[AttendeeService, Depends(get_attendee_service)], current_user: Annotated[UserEntity, Depends(get_current_user)]):
    """Cancel the current user's registration."""
    try:
        attendee = attendee_service.unregister_from_event(user_id=current_user.id, event_id=event_id)
        return {"message": "Successfully unregistered", "status": attendee.status.value}
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get("/users/me/events", response_model=list[EventResponse])
def get_my_events(attendee_service: Annotated[AttendeeService, Depends(get_attendee_service)], event_service: Annotated[EventService, Depends(get_event_service)], current_user: Annotated[UserEntity, Depends(get_current_user)]):
    """List all events the current user is registered to."""
    event_ids = attendee_service.get_user_events(user_id=current_user.id)
    events = []
    for eid in event_ids:
        try:
            event = event_service.get_event(eid)
            events.append(EventResponse.model_validate(event.model_dump()))
        except EntityNotFoundException:
            continue
    return events


@router.get("/events/{event_id}/attendees", response_model=AttendeeListResponse)
def list_event_attendees(event_id: int, attendee_service: Annotated[AttendeeService, Depends(get_attendee_service)], current_user: Annotated[UserEntity, Depends(get_current_organizer_or_admin)], page: int = Query(default=1, ge=1), size: int = Query(default=100, ge=1, le=100)):
    """List all attendees for an event (Organizer/Admin only)."""
    attendees, total = attendee_service.get_event_attendees(event_id, page=page, size=size)
    return AttendeeListResponse(attendees=[AttendeeResponse.model_validate(a.model_dump()) for a in attendees], total=total)
