"""User domain entity. Pure Pydantic model, no DB dependencies."""

from datetime import datetime
from pydantic import BaseModel, Field
from app.domain.enums import UserRole


class UserEntity(BaseModel):
    """Core user entity representing a system user."""
    id: int | None = None
    email: str
    hashed_password: str = ""
    full_name: str
    role: UserRole = UserRole.ATTENDEE
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
