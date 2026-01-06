"""Shared exception hierarchy for ip_tools clients."""

from __future__ import annotations


class IpToolsError(Exception):
    """Base exception for all ip_tools errors."""


class ApiError(IpToolsError):
    """Base for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:
        base = super().__str__()
        if self.status_code:
            return f"{base} (HTTP {self.status_code})"
        return base


class NotFoundError(ApiError):
    """Resource not found (404)."""


class RateLimitError(ApiError):
    """Rate limit exceeded (429)."""


class AuthenticationError(ApiError):
    """Authentication failed (401/403)."""


class ServerError(ApiError):
    """Server-side error (5xx)."""


class ValidationError(IpToolsError, ValueError):
    """Input validation failed.

    Inherits from ValueError for backward compatibility with code
    that catches ValueError for validation errors.
    """


class ConfigurationError(IpToolsError):
    """Missing or invalid configuration (e.g., API keys)."""


class ParseError(IpToolsError):
    """Failed to parse response data (XML, JSON, HTML, etc.)."""

    def __init__(
        self,
        message: str,
        source: str | None = None,
        raw_content: str | None = None,
    ) -> None:
        super().__init__(message)
        self.source = source
        self.raw_content = raw_content


__all__ = [
    "IpToolsError",
    "ApiError",
    "NotFoundError",
    "RateLimitError",
    "AuthenticationError",
    "ServerError",
    "ValidationError",
    "ConfigurationError",
    "ParseError",
]
