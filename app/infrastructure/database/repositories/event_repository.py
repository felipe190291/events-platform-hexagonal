"""SQLModel event repository implementation."""

from sqlmodel import Session, select, func, col
from app.domain.entities.event import EventEntity
from app.domain.enums import EventStatus, AttendeeStatus
from app.domain.ports.event_repository import EventRepositoryPort
from app.infrastructure.database.models import EventModel, AttendeeModel


class SQLModelEventRepository(EventRepositoryPort):
    """Concrete implementation of EventRepositoryPort using SQLModel."""

    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: EventModel, attendee_count: int = 0) -> EventEntity:
        return EventEntity(
            id=model.id,
            title=model.title,
            description=model.description,
            location=model.location,
            start_date=model.start_date,
            end_date=model.end_date,
            capacity=model.capacity,
            status=model.status,
            image_url=model.image_url,
            organizer_id=model.organizer_id,
            created_at=model.created_at,
            attendee_count=attendee_count,
        )

    def _get_attendee_count(self, event_id: int) -> int:
        statement = select(func.count(AttendeeModel.id)).where(
            AttendeeModel.event_id == event_id,
            AttendeeModel.status == AttendeeStatus.REGISTERED,
        )
        return self._session.exec(statement).one()

    def create(self, event: EventEntity) -> EventEntity:
        db_event = EventModel(
            title=event.title,
            description=event.description,
            location=event.location,
            start_date=event.start_date,
            end_date=event.end_date,
            capacity=event.capacity,
            status=event.status,
            image_url=event.image_url,
            organizer_id=event.organizer_id,
            created_at=event.created_at,
        )
        self._session.add(db_event)
        self._session.commit()
        self._session.refresh(db_event)
        return self._to_entity(db_event)

    def get_by_id(self, event_id: int) -> EventEntity | None:
        db_event = self._session.get(EventModel, event_id)
        if not db_event:
            return None
        count = self._get_attendee_count(event_id)
        return self._to_entity(db_event, attendee_count=count)

    def search(
        self,
        query: str | None = None,
        status: EventStatus | None = None,
        organizer_id: int | None = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[EventEntity], int]:
        statement = select(EventModel)
        count_statement = select(func.count(EventModel.id))

        if query:
            search_filter = col(EventModel.title).ilike(f"%{query}%")
            statement = statement.where(search_filter)
            count_statement = count_statement.where(search_filter)

        if status:
            statement = statement.where(EventModel.status == status)
            count_statement = count_statement.where(EventModel.status == status)
            
        if organizer_id:
            statement = statement.where(EventModel.organizer_id == organizer_id)
            count_statement = count_statement.where(EventModel.organizer_id == organizer_id)

        total = self._session.exec(count_statement).one()

        statement = statement.offset(skip).limit(limit).order_by(EventModel.created_at.desc())
        db_events = self._session.exec(statement).all()

        events = []
        for db_event in db_events:
            count = self._get_attendee_count(db_event.id)
            events.append(self._to_entity(db_event, attendee_count=count))

        return events, total

    def get_by_organizer(self, organizer_id: int) -> list[EventEntity]:
        statement = select(EventModel).where(EventModel.organizer_id == organizer_id)
        db_events = self._session.exec(statement).all()
        return [self._to_entity(e, self._get_attendee_count(e.id)) for e in db_events]

    def update(self, event: EventEntity) -> EventEntity:
        db_event = self._session.get(EventModel, event.id)
        if not db_event:
            return event
        db_event.title = event.title
        db_event.description = event.description
        db_event.location = event.location
        db_event.start_date = event.start_date
        db_event.end_date = event.end_date
        db_event.capacity = event.capacity
        db_event.status = event.status
        db_event.image_url = event.image_url
        self._session.add(db_event)
        self._session.commit()
        self._session.refresh(db_event)
        count = self._get_attendee_count(db_event.id)
        return self._to_entity(db_event, attendee_count=count)

    def delete(self, event_id: int) -> bool:
        db_event = self._session.get(EventModel, event_id)
        if not db_event:
            return False
        self._session.delete(db_event)
        self._session.commit()
        return True
