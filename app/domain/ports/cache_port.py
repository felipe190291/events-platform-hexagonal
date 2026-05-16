"""Cache port definition."""

from abc import ABC, abstractmethod
from typing import Any


class CachePort(ABC):
    """Abstract port for cache operations."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Retrieve a cached value by its key."""
        ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 60) -> None:
        """Store a value in the cache with an expiration time."""
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove a specific key from the cache."""
        ...

    @abstractmethod
    def delete_pattern(self, pattern: str) -> None:
        """Remove all keys matching a pattern."""
        ...
