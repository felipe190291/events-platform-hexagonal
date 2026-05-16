"""Authentication service orchestrating registration and login."""

from app.domain.entities.user import UserEntity
from app.domain.enums import UserRole
from app.domain.exceptions import (
    AuthenticationException,
    DuplicateEntityException,
    EntityNotFoundException,
)
from app.domain.ports.user_repository import UserRepositoryPort
from app.infrastructure.security.jwt_handler import (
    create_access_token,
    hash_password,
    verify_password,
)


class AuthService:
    """Orchestrates authentication-related business operations."""

    def __init__(self, user_repo: UserRepositoryPort):
        self._user_repo = user_repo

    def register(self, email: str, password: str, full_name: str, role: UserRole = UserRole.ATTENDEE) -> UserEntity:
        """Register a new user in the system."""
        existing = self._user_repo.get_by_email(email)
        if existing:
            raise DuplicateEntityException("User", "email", email)

        user = UserEntity(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
        )
        return self._user_repo.create(user)

    def login(self, email: str, password: str) -> tuple[UserEntity, str, str]:
        """Authenticate a user and generate tokens."""
        user = self._user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationException("Invalid email or password")

        if not user.is_active:
            raise AuthenticationException("Account is disabled")

        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        refresh_token = create_access_token(
            data={"sub": str(user.id)}, 
            token_type="refresh"
        )
        return user, access_token, refresh_token

    def refresh_tokens(self, user_id: int) -> tuple[str, str]:
        """Generate new access and refresh tokens for a user."""
        user = self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationException("User not found or inactive")

        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        refresh_token = create_access_token(
            data={"sub": str(user.id)}, 
            token_type="refresh"
        )
        return access_token, refresh_token

    def get_current_user(self, user_id: int) -> UserEntity:
        """Retrieve the currently authenticated user's profile."""
        user = self._user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException("User", user_id)
        return user
