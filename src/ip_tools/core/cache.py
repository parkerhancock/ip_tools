"""Shared HTTP caching helpers for ip_tools clients."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import httpx
from hishel import AsyncSqliteStorage  # type: ignore[attr-defined]
from hishel.httpx import AsyncCacheClient  # type: ignore[attr-defined]
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential_jitter


class RetryingAsyncSqliteStorage(AsyncSqliteStorage):
    """SQLite-backed cache storage that retries when the DB is locked."""

    def __init__(self, *args: Any, max_attempts: int = 5, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._max_attempts = max_attempts
        self._pragmas_set = False

    def _retryer(self) -> AsyncRetrying:
        return AsyncRetrying(
            stop=stop_after_attempt(self._max_attempts),
            wait=wait_exponential_jitter(initial=0.1, max=2.0),
            reraise=True,
        )

    async def _ensure_connection(self):  # type: ignore[override]
        connection = await super()._ensure_connection()
        if not self._pragmas_set:
            cursor = await connection.cursor()
            await cursor.execute("PRAGMA journal_mode=WAL")
            await cursor.execute("PRAGMA synchronous=NORMAL")
            await cursor.execute("PRAGMA busy_timeout=5000")
            await connection.commit()
            self._pragmas_set = True
        return connection

    async def create_entry(self, *args: Any, **kwargs: Any):  # type: ignore[override]
        async for attempt in self._retryer():
            with attempt:
                return await super().create_entry(*args, **kwargs)

    async def get_entries(self, *args: Any, **kwargs: Any):  # type: ignore[override]
        async for attempt in self._retryer():
            with attempt:
                return await super().get_entries(*args, **kwargs)

    async def _batch_cleanup(self, *args: Any, **kwargs: Any):  # type: ignore[override]
        async for attempt in self._retryer():
            with attempt:
                return await super()._batch_cleanup(*args, **kwargs)


def build_cached_http_client(
    *,
    use_cache: bool,
    cache_name: str,
    headers: Mapping[str, str] | None = None,
    **client_kwargs: Any,
) -> httpx.AsyncClient:
    """Return an AsyncClient that shares the retrying SQLite cache."""

    default_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    merged_headers = dict(default_headers)
    if headers:
        merged_headers.update(headers)

    if not use_cache:
        return httpx.AsyncClient(headers=merged_headers, **client_kwargs)

    cache_root = Path.home() / ".cache" / "ip_tools"
    cache_root.mkdir(parents=True, exist_ok=True)
    storage = RetryingAsyncSqliteStorage(database_path=str(cache_root / f"{cache_name}.db"))
    return AsyncCacheClient(  # type: ignore[misc]
        headers=merged_headers,
        storage=storage,
        **client_kwargs,
    )


__all__ = ["build_cached_http_client"]
