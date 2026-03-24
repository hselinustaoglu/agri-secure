"""Base async HTTP client with Redis caching and error handling."""

import logging
from typing import Any, Optional

import httpx

from .cache import RedisCache

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 30.0


class BaseExternalClient:
    """Base class for all external API clients.

    Subclasses receive a shared async httpx client and a Redis cache.
    All HTTP calls are wrapped with timeout and error handling.
    """

    def __init__(self, redis_url: str, base_url: str = "", ttl: int = 3600) -> None:
        self.base_url = base_url.rstrip("/")
        self.ttl = ttl
        self.cache = RedisCache(redis_url)

    # ── Cache helpers ──────────────────────────────────────────────────────

    def _cache_get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)

    def _cache_set(self, key: str, value: Any) -> None:
        self.cache.set(key, value, self.ttl)

    # ── HTTP helpers ───────────────────────────────────────────────────────

    async def _get(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> Any:
        """Perform an async GET and return the parsed JSON body.

        Raises ``httpx.HTTPStatusError`` on 4xx/5xx responses and
        ``httpx.TimeoutException`` on timeout.
        """
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def _get_bytes(
        self,
        url: str,
        params: Optional[dict] = None,
        timeout: float = 120.0,
    ) -> bytes:
        """Perform an async GET and return raw bytes (e.g. for binary files)."""
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.content
