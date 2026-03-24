"""Redis cache wrapper for Upstash (or any Redis-compatible backend)."""

import json
import logging
from typing import Any, Optional

import redis

logger = logging.getLogger(__name__)


class RedisCache:
    """Thin wrapper around Redis providing JSON get/set/invalidate with TTL support."""

    def __init__(self, redis_url: str) -> None:
        self._client: Optional[redis.Redis] = None
        self._redis_url = redis_url

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.Redis.from_url(
                self._redis_url, decode_responses=True, socket_connect_timeout=5
            )
        return self._client

    def get(self, key: str) -> Optional[Any]:
        """Return cached value (deserialized from JSON), or None on miss/error."""
        try:
            raw = self.client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            logger.warning("Cache GET failed for key=%s: %s", key, exc)
            return None

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Serialize value to JSON and store with TTL (seconds)."""
        try:
            self.client.setex(key, ttl, json.dumps(value))
        except Exception as exc:
            logger.warning("Cache SET failed for key=%s: %s", key, exc)

    def invalidate(self, key: str) -> None:
        """Delete a specific cache key."""
        try:
            self.client.delete(key)
        except Exception as exc:
            logger.warning("Cache DELETE failed for key=%s: %s", key, exc)

    def stats(self) -> dict:
        """Return basic Redis INFO stats (keyspace, memory), or empty dict on error."""
        try:
            info = self.client.info()
            return {
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "keyspace": info.get("db0"),
            }
        except Exception as exc:
            logger.warning("Cache stats failed: %s", exc)
            return {}
