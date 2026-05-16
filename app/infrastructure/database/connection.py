"""Database connection factory supporting SQLite and PostgreSQL."""

from sqlmodel import Session, SQLModel, create_engine
from app.config import get_settings


def _build_engine():
    """Build the SQLAlchemy engine based on the configured DATABASE_URL."""
    settings = get_settings()
    connect_args = {}

    if settings.is_sqlite:
        connect_args = {"check_same_thread": False}

    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        connect_args=connect_args,
    )
    return engine


engine = _build_engine()


def init_db() -> None:
    """Create all database tables defined by SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Provide a database session as a FastAPI dependency."""
    with Session(engine) as session:
        yield session
