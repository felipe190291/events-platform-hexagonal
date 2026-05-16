"""SQLModel attendee repository implementation."""

from sqlmodel import Session, select, func
from app.domain.entities.attendee import AttendeeEntity
from app.domain.enums import AttendeeStatus
from app.domain.ports.attendee_repository import AttendeeRepositoryPort
from app.infrastructure.database.models import AttendeeModel


class SQLModelAttendeeRepository(AttendeeRepositoryPort):
    """Concrete implementation of AttendeeRepositoryPort using SQLModel."""

    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: AttendeeModel) -> AttendeeEntity:
        return AttendeeEntity(
            id=model.id,
            user_id=model.user_id,
            event_id=model.event_id,
            registered_at=model.registered_at,
            status=model.status,
        )

    def create(self, attendee: AttendeeEntity) -> AttendeeEntity:
        db_attendee = AttendeeModel(
            user_id=attendee.user_id,
            event_id=attendee.event_id,
            registered_at=attendee.registered_at,
            status=attendee.status,
        )
        self._session.add(db_attendee)
        self._session.commit()
        self._session.refresh(db_attendee)
        return self._to_entity(db_attendee)

    def get_by_user_and_event(self, user_id: int, event_id: int) -> AttendeeEntity | None:
        statement = select(AttendeeModel).where(
            AttendeeModel.user_id == user_id,
            AttendeeModel.event_id == event_id,
        )
        db_attendee = self._session.exec(statement).first()
        return self._to_entity(db_attendee) if db_attendee else None

    def get_by_event(self, event_id: int, skip: int = 0, limit: int = 100) -> tuple[list[AttendeeEntity], int]:
        count_stmt = select(func.count(AttendeeModel.id)).where(
            AttendeeModel.event_id == event_id,
            AttendeeModel.status == AttendeeStatus.REGISTERED,
        )
        total = self._session.exec(count_stmt).one()

        statement = (
            select(AttendeeModel)
            .where(
                AttendeeModel.event_id == event_id,
                AttendeeModel.status == AttendeeStatus.REGISTERED,
            )
            .offset(skip)
            .limit(limit)
        )
        db_attendees = self._session.exec(statement).all()
        return [self._to_entity(a) for a in db_attendees], total

    def get_events_by_user(self, user_id: int) -> list[int]:
        statement = select(AttendeeModel.event_id).where(
            AttendeeModel.user_id == user_id,
            AttendeeModel.status == AttendeeStatus.REGISTERED,
        )
        return list(self._session.exec(statement).all())

    def update(self, attendee: AttendeeEntity) -> AttendeeEntity:
        db_attendee = self._session.get(AttendeeModel, attendee.id)
        if not db_attendee:
            return attendee
        db_attendee.status = attendee.status
        self._session.add(db_attendee)
        self._session.commit()
        self._session.refresh(db_attendee)
        return self._to_entity(db_attendee)

    def count_by_event(self, event_id: int) -> int:
        statement = select(func.count(AttendeeModel.id)).where(
            AttendeeModel.event_id == event_id,
            AttendeeModel.status == AttendeeStatus.REGISTERED,
        )
        return self._session.exec(statement).one()
