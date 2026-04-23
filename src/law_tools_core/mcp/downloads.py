"""Download registry with HMAC-signed resource URIs.

Search/list tools return signed download URLs on records that have
downloadable content (PDFs, filings, attachments). Example::

    https://mcp.example.com/downloads/uspto/applications/16123456/documents/XYZ?key=<hmac>

When a client hits the URL, the server verifies the HMAC, fetches the
document via a connector-registered fetcher (with disk caching), and
streams it back.

Resource paths are designed to map to future MCP resource templates::

    patent-client-agents://uspto/applications/{app_number}/documents/{doc_id}

Two rules govern how tool responses handle URLs:

    1. MASK INACCESSIBLE URLs. Any URL in a tool response that requires
       auth the agent doesn't have (API keys, tokens in our .env) must
       be removed.
    2. ADD DOWNLOAD URLs. When a search/list result has downloadable
       content, add a ``download_url`` field using
       ``build_download_url()``. Register a fetch function via
       ``register_source()``, and remove the dedicated download_* tool.

Env vars (all accept a ``LAW_TOOLS_*`` legacy alias)::

    LAW_TOOLS_CORE_PUBLIC_URL        base URL for download links
    LAW_TOOLS_CORE_API_KEY           secret for HMAC signing
    LAW_TOOLS_CORE_DOWNLOAD_CACHE    on-disk cache dir (default: ~/.cache/law_tools_core/downloads)
    LAW_TOOLS_CORE_DOWNLOAD_TTL_SECONDS  HMAC rotation bucket (default 86400)
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import tempfile
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from starlette.requests import Request
from starlette.responses import Response

from . import _env


def _public_url() -> str:
    return _env.get("PUBLIC_URL", "").rstrip("/")


def _secret() -> str:
    return _env.get("API_KEY", "")


def _cache_dir() -> Path:
    custom = _env.get("DOWNLOAD_CACHE")
    if custom:
        return Path(custom)
    return Path.home() / ".cache" / "law_tools_core" / "downloads"


def _key_rotation_seconds() -> int:
    return int(_env.get("DOWNLOAD_TTL_SECONDS", "86400"))


_PERMANENT_BUCKET = "permanent"  # sentinel for non-expiring URLs


# ---------------------------------------------------------------------------
# HMAC signing
# ---------------------------------------------------------------------------


def _current_bucket() -> int:
    """Wall-clock bucket index for the current rotation window."""
    return int(time.time()) // _key_rotation_seconds()


def _bucket_expiry_epoch(bucket: int) -> int:
    """Unix epoch at which a URL signed with ``bucket`` definitively expires.

    A URL is valid while either ``current_bucket`` or ``current_bucket - 1``
    matches the signed bucket — so the latest moment a ``bucket``-signed
    URL still works is the end of the bucket immediately following it.
    """
    return (bucket + 2) * _key_rotation_seconds()


def sign_path(path: str, *, bucket: int | str | None = None) -> str:
    """HMAC-SHA256 of ``{path}|{bucket}``, truncated to 12 URL-safe base64 chars.

    ``bucket`` defaults to the current rotation bucket — so the same
    path mints a different signature each rotation window. Pass an
    explicit integer for testing, or the string ``"permanent"`` for a
    URL that never expires (the sentinel is also accepted by
    ``verify_path``).
    """
    if bucket is None:
        bucket = _current_bucket()
    payload = f"{path}|{bucket}".encode()
    sig = hmac.new(_secret().encode(), payload, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig[:9]).rstrip(b"=").decode()  # 9 bytes → 12 chars


def verify_path(path: str, signature: str) -> bool:
    """Constant-time HMAC verification.

    A URL is valid if its signature matches the current rotation bucket,
    the previous bucket (grace window for URLs minted near a boundary),
    or the special ``"permanent"`` bucket. There is no ``exp`` query
    parameter — the time dimension lives inside the HMAC. The agent
    reads ``expires_at`` from the tool response to know when to re-call.
    """
    if not _secret():
        return True  # no secret configured (local/stdio mode)
    current = _current_bucket()
    candidate_buckets: tuple[int | str, ...] = (current, current - 1, _PERMANENT_BUCKET)
    for bucket in candidate_buckets:
        expected = sign_path(path, bucket=bucket)
        if hmac.compare_digest(expected, signature):
            return True
    return False


# ---------------------------------------------------------------------------
# Disk cache
# ---------------------------------------------------------------------------


def _cache_key(resource_path: str) -> Path:
    digest = hashlib.sha256(resource_path.encode()).hexdigest()[:16]
    return _cache_dir() / digest


def _cache_get(resource_path: str) -> tuple[bytes, str | None] | None:
    """Return ``(content, filename)`` if cached, else ``None``.

    Filename is read from a ``.name`` sidecar written by ``_cache_put``
    and is used to set Content-Disposition when streaming cached
    content.
    """
    path = _cache_key(resource_path)
    if not path.exists():
        return None
    name_path = path.with_suffix(".name")
    filename = name_path.read_text() if name_path.exists() else None
    return path.read_bytes(), filename


def _cache_put(resource_path: str, content: bytes, filename: str | None = None) -> None:
    _cache_dir().mkdir(parents=True, exist_ok=True)
    key = _cache_key(resource_path)
    key.write_bytes(content)
    if filename:
        key.with_suffix(".name").write_text(filename)


# ---------------------------------------------------------------------------
# Source registry
# ---------------------------------------------------------------------------


@dataclass
class DownloadSource:
    """A registered download source."""

    fetch: Callable[..., Awaitable[tuple[bytes, str]]]  # (content, filename)
    mime_type: str = "application/pdf"
    path_prefix: str = ""


# Maps path prefixes to sources. Matched by longest prefix.
_SOURCES: dict[str, DownloadSource] = {}


def register_source(
    path_prefix: str,
    fetch: Callable[..., Awaitable[tuple[bytes, str]]],
    mime_type: str = "application/pdf",
) -> None:
    """Register a download source for a path prefix.

    Connectors call this at module import to make their content
    retrievable through the shared ``/downloads/{resource_path}`` route.
    Idempotent — re-registering the same prefix replaces the entry.
    """
    _SOURCES[path_prefix] = DownloadSource(
        fetch=fetch, mime_type=mime_type, path_prefix=path_prefix
    )


def _match_source(resource_path: str) -> tuple[DownloadSource, str] | None:
    """Find the source matching a resource path.

    Returns ``(source, remaining_path)`` or ``None`` if unknown.
    Longest-prefix match.
    """
    for prefix in sorted(_SOURCES, key=len, reverse=True):
        if resource_path.startswith(prefix + "/") or resource_path == prefix:
            remainder = resource_path[len(prefix) :].lstrip("/")
            return _SOURCES[prefix], remainder
    return None


# ---------------------------------------------------------------------------
# URL builder (called by tools)
# ---------------------------------------------------------------------------


def build_download_url(
    resource_path: str,
    *,
    label: str = "",
    permanent: bool = False,
) -> str:
    """Build a signed download URL (remote) or resource-path stub (local).

    The URL is signed against the current rotation bucket and is valid
    for at least ``LAW_TOOLS_CORE_DOWNLOAD_TTL_SECONDS`` (default 24h),
    up to ~2× that depending on minting time relative to the bucket
    boundary. No ``exp`` query parameter — the time dimension is bound
    inside the HMAC, so the URL is just ``?key={sig}``.

    Args:
        resource_path: Resource path (e.g. ``"uspto/applications/16123456/documents/XYZ"``)
        label: Human-readable description for the return message
        permanent: Mint a URL that never expires. Use sparingly —
            leaks are valid until ``LAW_TOOLS_CORE_API_KEY`` rotates.
    """
    resource_path = resource_path.strip("/")
    public = _public_url()

    if public:
        bucket: int | str | None = _PERMANENT_BUCKET if permanent else None
        sig = sign_path(resource_path, bucket=bucket)
        url = f"{public}/downloads/{resource_path}?key={sig}"
        if label:
            return f"{label}\n\nDownload: {url}"
        return url

    # Local/stdio fallback: tools handle their own tempfiles
    return f"(local mode) Resource: {resource_path}"


async def build_download_url_or_fetch(
    resource_path: str,
    *,
    label: str = "",
) -> str:
    """Build a signed URL, or fetch + save to tempfile for local mode.

    Async version that actually fetches in local mode.
    """
    resource_path = resource_path.strip("/")
    public = _public_url()

    if public:
        sig = sign_path(resource_path)
        url = f"{public}/downloads/{resource_path}?key={sig}"
        if label:
            return f"{label}\n\nDownload: {url}"
        return url

    match = _match_source(resource_path)
    if match is None:
        raise ValueError(f"Unknown download source for path: {resource_path}")

    source, remainder = match
    content, filename = await source.fetch(remainder)

    suffix = Path(filename).suffix or ".pdf"
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, prefix="law_tools_core_")
    tmp.write(content)
    tmp.close()

    size_str = f"{len(content):,} bytes"
    if label:
        return f"Downloaded {label} ({size_str}). Saved to {tmp.name}"
    return f"Downloaded file ({size_str}). Saved to {tmp.name}"


def download_response(
    resource_path: str,
    content: bytes,
    *,
    filename: str,
    content_type: str = "application/pdf",
    permanent: bool = False,
    **extras: object,
) -> dict:
    """Standard return shape for MCP download tools.

    Caches ``content`` so the URL hit serves from disk, then returns the
    canonical payload: ``download_url``, ``expires_at``, ``filename``,
    ``content_type``, ``size_bytes``, plus any ``extras`` (e.g.
    ``patent_number``).

    ``expires_at`` is an ISO 8601 UTC timestamp telling the agent the
    *guaranteed* deadline — the URL is good through that moment and
    refused afterward. (The actual upper bound can be the same instant
    or up to one rotation window later, depending on when in the bucket
    cycle the URL was minted; the response always reports the latest
    moment the URL is *guaranteed* to still work.)

    Pass ``permanent=True`` to mint a non-expiring URL (omits
    ``expires_at``); use sparingly because leaks become permanent until
    ``LAW_TOOLS_CORE_API_KEY`` rotates.

    In remote/HTTP mode (``LAW_TOOLS_CORE_PUBLIC_URL`` set) the response
    carries a signed ``download_url``. In local/stdio mode the bytes
    are written to a tempfile and ``file_path`` is returned instead —
    tempfiles do not expire. No base64 in either case.
    """
    payload: dict = {
        "filename": filename,
        "content_type": content_type,
        "size_bytes": len(content),
        **extras,
    }
    if _public_url():
        _cache_put(resource_path, content, filename=filename)
        payload["download_url"] = build_download_url(resource_path, permanent=permanent)
        if not permanent:
            expiry = _bucket_expiry_epoch(_current_bucket())
            payload["expires_at"] = datetime.fromtimestamp(expiry, tz=UTC).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
    else:
        suffix = Path(filename).suffix or ".bin"
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, prefix="law_tools_core_")
        tmp.write(content)
        tmp.close()
        payload["file_path"] = tmp.name
    return payload


# ---------------------------------------------------------------------------
# Route handler (registered in server_factory.build_server)
# ---------------------------------------------------------------------------


async def handle_download(request: Request) -> Response:
    """Handle GET ``/downloads/{resource_path}?key={hmac_signature}``."""
    resource_path: str = request.path_params.get("path", "")
    if not resource_path:
        return Response("Missing resource path", status_code=400)

    # Verify HMAC. Time/expiry is bound inside the HMAC (rotating-key
    # scheme), so there's no separate `exp` query parameter — an
    # expired URL simply fails to verify.
    signature = request.query_params.get("key", "")
    if not verify_path(resource_path, signature):
        return Response(
            "Invalid signature, or URL has expired (URLs rotate every "
            f"{_key_rotation_seconds()}s; re-call the tool to mint a fresh one).",
            status_code=403,
        )

    cached = _cache_get(resource_path)
    if cached is not None:
        content, cached_filename = cached
        source_match = _match_source(resource_path)
        mime = source_match[0].mime_type if source_match else "application/octet-stream"
        disposition = (
            f'attachment; filename="{cached_filename}"' if cached_filename else "attachment"
        )
        return Response(
            content=content,
            media_type=mime,
            headers={
                "Content-Disposition": disposition,
                "Cache-Control": "private, max-age=3600",
            },
        )

    match = _match_source(resource_path)
    if match is None:
        return Response(f"Unknown resource: {resource_path}", status_code=404)

    source, remainder = match
    try:
        content, filename = await source.fetch(remainder)
    except PermissionError as exc:
        return Response(str(exc), status_code=410)
    except Exception as exc:
        return Response(f"Fetch error: {exc}", status_code=502)

    _cache_put(resource_path, content, filename=filename)

    return Response(
        content=content,
        media_type=source.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "private, max-age=3600",
        },
    )
