"""In-memory cache adapter."""

import json
import time
from typing import Any
from app.domain.ports.cache_port import CachePort


class InMemoryCacheAdapter(CachePort):
    """Simple dictionary-based cache for development."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        if key not in self._store:
            return None

        value, expiry = self._store[key]
        if time.time() > expiry:
            del self._store[key]
            return None

        return json.loads(value) if isinstance(value, str) else value

    def set(self, key: str, value: Any, ttl: int = 60) -> None:
        expiry = time.time() + ttl
        serialized = json.dumps(value) if not isinstance(value, str) else value
        self._store[key] = (serialized, expiry)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def delete_pattern(self, pattern: str) -> None:
        import fnmatch
        keys_to_delete = [k for k in self._store if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            del self._store[key]
