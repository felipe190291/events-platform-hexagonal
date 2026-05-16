"""SQLModel user repository implementation."""

from sqlmodel import Session, select
from app.domain.entities.user import UserEntity
from app.domain.ports.user_repository import UserRepositoryPort
from app.infrastructure.database.models import UserModel


class SQLModelUserRepository(UserRepositoryPort):
    """Concrete implementation of UserRepositoryPort using SQLModel."""

    def __init__(self, session: Session):
        self._session = session

    def _to_entity(self, model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            role=model.role,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    def _to_model(self, entity: UserEntity) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            hashed_password=entity.hashed_password,
            full_name=entity.full_name,
            role=entity.role,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )

    def create(self, user: UserEntity) -> UserEntity:
        db_user = self._to_model(user)
        self._session.add(db_user)
        self._session.commit()
        self._session.refresh(db_user)
        return self._to_entity(db_user)

    def get_by_id(self, user_id: int) -> UserEntity | None:
        db_user = self._session.get(UserModel, user_id)
        return self._to_entity(db_user) if db_user else None

    def get_by_email(self, email: str) -> UserEntity | None:
        statement = select(UserModel).where(UserModel.email == email)
        db_user = self._session.exec(statement).first()
        return self._to_entity(db_user) if db_user else None

    def search(self, query: str | None = None, role: str | None = None, skip: int = 0, limit: int = 100) -> tuple[list[UserEntity], int]:
        from sqlmodel import col, func, or_
        statement = select(UserModel)
        count_statement = select(func.count()).select_from(UserModel)

        if query:
            filter_stmt = or_(
                col(UserModel.full_name).ilike(f"%{query}%"),
                col(UserModel.email).ilike(f"%{query}%")
            )
            statement = statement.where(filter_stmt)
            count_statement = count_statement.where(filter_stmt)
            
        if role:
            statement = statement.where(UserModel.role == role)
            count_statement = count_statement.where(UserModel.role == role)

        total = self._session.exec(count_statement).one()
        statement = statement.offset(skip).limit(limit).order_by(UserModel.created_at.desc())
        db_users = self._session.exec(statement).all()
        
        return [self._to_entity(u) for u in db_users], total

    def get_all(self, skip: int = 0, limit: int = 100) -> list[UserEntity]:
        statement = select(UserModel).offset(skip).limit(limit)
        db_users = self._session.exec(statement).all()
        return [self._to_entity(u) for u in db_users]

    def update(self, user: UserEntity) -> UserEntity:
        db_user = self._session.get(UserModel, user.id)
        if not db_user:
            return user
        db_user.email = user.email
        db_user.full_name = user.full_name
        db_user.role = user.role
        db_user.is_active = user.is_active
        if user.hashed_password:
            db_user.hashed_password = user.hashed_password
        self._session.add(db_user)
        self._session.commit()
        self._session.refresh(db_user)
        return self._to_entity(db_user)

    def delete(self, user_id: int) -> bool:
        db_user = self._session.get(UserModel, user_id)
        if not db_user:
            return False
        self._session.delete(db_user)
        self._session.commit()
        return True

    def count(self) -> int:
        from sqlmodel import func
        statement = select(func.count()).select_from(UserModel)
        return self._session.exec(statement).one()
