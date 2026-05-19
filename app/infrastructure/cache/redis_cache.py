"""Redis cache adapter."""

import json
from typing import Any
import redis
from app.config import get_settings
from app.domain.ports.cache_port import CachePort


class RedisCacheAdapter(CachePort):
    """Production-ready Redis cache implementation."""

    def __init__(self):
        settings = get_settings()
        self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def get(self, key: str) -> Any | None:
        value = self._client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def set(self, key: str, value: Any, ttl: int = 60) -> None:
        import datetime
        def json_serial(obj):
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
            
        serialized = json.dumps(value, default=json_serial)
        self._client.setex(key, ttl, serialized)

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def delete_pattern(self, pattern: str) -> None:
        cursor = 0
        while True:
            cursor, keys = self._client.scan(cursor, match=pattern, count=100)
            if keys:
                self._client.delete(*keys)
            if cursor == 0:
                break
