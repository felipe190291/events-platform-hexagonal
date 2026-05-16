"""SQLModel session repository implementation."""

from datetime import datetime
from sqlmodel import Session, select, and_
from app.domain.entities.session import SessionEntity
from app.domain.ports.session_repository import SessionRepositoryPort
from app.infrastructure.database.models import SessionModel


class SQLModelSessionRepository(SessionRepositoryPort):
    """Concrete implementation of SessionRepositoryPort using SQLModel."""

    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: SessionModel) -> SessionEntity:
        return SessionEntity(
            id=model.id,
            title=model.title,
            description=model.description,
            speaker_name=model.speaker_name,
            start_time=model.start_time,
            end_time=model.end_time,
            event_id=model.event_id,
        )

    def create(self, session_entity: SessionEntity) -> SessionEntity:
        db_session = SessionModel(
            title=session_entity.title,
            description=session_entity.description,
            speaker_name=session_entity.speaker_name,
            start_time=session_entity.start_time,
            end_time=session_entity.end_time,
            event_id=session_entity.event_id,
        )
        self._session.add(db_session)
        self._session.commit()
        self._session.refresh(db_session)
        return self._to_entity(db_session)

    def get_by_id(self, session_id: int) -> SessionEntity | None:
        db_session = self._session.get(SessionModel, session_id)
        return self._to_entity(db_session) if db_session else None

    def get_by_event(self, event_id: int) -> list[SessionEntity]:
        statement = (
            select(SessionModel)
            .where(SessionModel.event_id == event_id)
            .order_by(SessionModel.start_time)
        )
        db_sessions = self._session.exec(statement).all()
        return [self._to_entity(s) for s in db_sessions]

    def update(self, session_entity: SessionEntity) -> SessionEntity:
        db_session = self._session.get(SessionModel, session_entity.id)
        if not db_session:
            return session_entity
        db_session.title = session_entity.title
        db_session.description = session_entity.description
        db_session.speaker_name = session_entity.speaker_name
        db_session.start_time = session_entity.start_time
        db_session.end_time = session_entity.end_time
        self._session.add(db_session)
        self._session.commit()
        self._session.refresh(db_session)
        return self._to_entity(db_session)

    def delete(self, session_id: int) -> bool:
        db_session = self._session.get(SessionModel, session_id)
        if not db_session:
            return False
        self._session.delete(db_session)
        self._session.commit()
        return True

    def check_time_overlap(
        self, event_id: int, start_time: datetime, end_time: datetime, exclude_id: int | None = None
    ) -> bool:
        statement = select(SessionModel).where(
            and_(
                SessionModel.event_id == event_id,
                SessionModel.start_time < end_time,
                SessionModel.end_time > start_time,
            )
        )
        if exclude_id:
            statement = statement.where(SessionModel.id != exclude_id)

        result = self._session.exec(statement).first()
        return result is not None
