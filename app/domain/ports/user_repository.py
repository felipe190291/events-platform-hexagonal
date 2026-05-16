"""User repository port definition."""

from abc import ABC, abstractmethod
from app.domain.entities.user import UserEntity


class UserRepositoryPort(ABC):
    """Abstract port for user data access operations."""

    @abstractmethod
    def create(self, user: UserEntity) -> UserEntity:
        """Persist a new user and return it with the generated ID."""
        ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> UserEntity | None:
        """Retrieve a user by their unique identifier."""
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity | None:
        """Retrieve a user by their email address."""
        ...

    @abstractmethod
    def search(self, query: str | None = None, role: str | None = None, skip: int = 0, limit: int = 100) -> tuple[list[UserEntity], int]:
        """Search users by name or email with optional role filter and pagination."""
        ...

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> list[UserEntity]:
        """Retrieve a paginated list of all users."""
        ...

    @abstractmethod
    def update(self, user: UserEntity) -> UserEntity:
        """Update an existing user's data."""
        ...

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete a user by their ID."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the total number of users in the system."""
        ...
