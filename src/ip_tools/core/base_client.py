"""Base async HTTP client with standardized patterns."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Self

import httpx

from .cache import build_cached_http_client
from .exceptions import (
    ApiError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from .resilience import default_retryer


class BaseAsyncClient:
    """Base class for async API clients with caching and retry support.

    Subclasses should override:
        - DEFAULT_BASE_URL: The default API base URL
        - CACHE_NAME: Name for the cache database file

    Example:
        class MyApiClient(BaseAsyncClient):
            DEFAULT_BASE_URL = "https://api.example.com"
            CACHE_NAME = "my_api"

            async def get_resource(self, id: str) -> dict:
                return await self._request_json("GET", f"/resources/{id}")
    """

    DEFAULT_BASE_URL: str = ""
    CACHE_NAME: str = "default"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        cache_path: Path | None = None,
        client: httpx.AsyncClient | None = None,
        use_cache: bool = True,
        max_retries: int = 4,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            base_url: Override the default base URL.
            cache_path: Custom path for the cache directory.
            client: Existing httpx.AsyncClient to use (for testing).
            use_cache: Whether to enable HTTP caching.
            max_retries: Maximum retry attempts for transient failures.
            headers: Additional headers to include in requests.
        """
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self._owns_client = client is None
        self._max_retries = max_retries

        if client is None:
            cache_dir = cache_path or Path.home() / ".cache" / "ip_tools"
            cache_dir.mkdir(parents=True, exist_ok=True)
            self._client = build_cached_http_client(
                use_cache=use_cache,
                cache_name=self.CACHE_NAME,
                headers=headers or {},
                follow_redirects=True,
            )
        else:
            self._client = client
            if headers:
                for key, value in headers.items():
                    self._client.headers.setdefault(key, value)

    async def close(self) -> None:
        """Close the underlying HTTP client if we own it."""
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    def _build_url(self, path: str) -> str:
        """Build a full URL from a path."""
        return f"{self.base_url}{path}"

    def _raise_for_status(self, response: httpx.Response, context: str = "") -> None:
        """Convert HTTP errors to typed exceptions.

        Args:
            response: The HTTP response to check.
            context: Optional context string for error messages.

        Raises:
            NotFoundError: For 404 responses.
            RateLimitError: For 429 responses.
            AuthenticationError: For 401/403 responses.
            ServerError: For 5xx responses.
            ApiError: For other non-success responses.
        """
        if response.is_success:
            return

        status = response.status_code
        body = response.text[:500] if response.text else ""
        msg = f"{context}: {status}" if context else f"HTTP {status}"

        if status == 404:
            raise NotFoundError(msg, status, body)
        if status == 429:
            raise RateLimitError(msg, status, body)
        if status in (401, 403):
            raise AuthenticationError(msg, status, body)
        if 500 <= status < 600:
            raise ServerError(msg, status, body)
        raise ApiError(msg, status, body)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        context: str = "",
        timeout: float | None = None,
    ) -> httpx.Response:
        """Make an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: URL path (will be appended to base_url).
            params: Query parameters.
            json: JSON body for POST/PUT requests.
            context: Context string for error messages.
            timeout: Optional request timeout in seconds.

        Returns:
            The HTTP response.

        Raises:
            ApiError: On non-retryable HTTP errors.
        """
        url = self._build_url(path)
        request_kwargs: dict[str, Any] = {}
        if params:
            request_kwargs["params"] = params
        if json:
            request_kwargs["json"] = json
        if timeout:
            request_kwargs["timeout"] = timeout

        async for attempt in default_retryer(max_attempts=self._max_retries):
            with attempt:
                response = await self._client.request(method, url, **request_kwargs)
                self._raise_for_status(response, context)
                return response

        # Should not reach here due to reraise=True in retryer
        raise RuntimeError("Unexpected retry exhaustion")

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        context: str = "",
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request and return JSON response.

        Args:
            method: HTTP method.
            path: URL path.
            params: Query parameters.
            json: JSON body.
            context: Context string for error messages.
            timeout: Optional request timeout.

        Returns:
            Parsed JSON response as a dictionary.
        """
        response = await self._request(
            method, path, params=params, json=json, context=context, timeout=timeout
        )
        return response.json()


__all__ = ["BaseAsyncClient"]
