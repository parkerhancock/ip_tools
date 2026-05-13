"""HTML → Pydantic transformers for WIPO Lex.

WIPO Lex serves all human-facing pages as server-rendered HTML.
``/results`` pages list legislation entries with a stable
``<a href="/wipolex/en/legislation/details/{ID}">{Title}</a>`` anchor shape;
detail pages carry the canonical metadata on OpenGraph and ``<meta name>``
tags plus a list of file attachments under known CSS classes.

The selectors here are intentionally minimal — the OpenGraph/meta layer is
the most stable surface WIPO offers. If/when WIPO renames their CSS
classes the meta tags survive; only the file-link selector needs updating.
"""

from __future__ import annotations

import re
from urllib.parse import urljoin

from lxml import html as _html

from .models import (
    LegislationDetail,
    LegislationSearchHit,
    LegislationSearchResponse,
    WipoLexFileLink,
)

_RESULT_HREF_RE = re.compile(r"/wipolex/[a-z]{2}/legislation/details/(\d+)")
_DETAIL_ID_RE = re.compile(r"/legislation/details/(\d+)")


def parse_legislation_search(
    html_text: str, base_url: str, query_url: str
) -> LegislationSearchResponse:
    """Parse a ``/wipolex/en/legislation/results`` HTML page into structured hits."""
    doc = _html.fromstring(html_text)
    seen: set[str] = set()
    hits: list[LegislationSearchHit] = []

    for anchor in doc.xpath("//a[contains(@href, '/legislation/details/')]"):
        href = anchor.get("href", "")
        match = _RESULT_HREF_RE.search(href)
        if not match:
            continue
        legislation_id = match.group(1)
        if legislation_id in seen:
            # WIPO Lex sometimes renders the same entry twice (mobile + desktop blocks).
            continue
        seen.add(legislation_id)
        title = " ".join((anchor.text_content() or "").split()).strip()
        if not title:
            continue
        hits.append(
            LegislationSearchHit(
                legislation_id=legislation_id,
                title=title,
                url=urljoin(base_url, href),
            )
        )

    return LegislationSearchResponse(hits=hits, query_url=query_url)


def parse_legislation_detail(
    html_text: str, base_url: str, *, legislation_id: str | None = None
) -> LegislationDetail:
    """Parse a ``/wipolex/en/legislation/details/{id}`` HTML page.

    Pass ``legislation_id`` when the caller already knows it (the
    ``WipoLexClient.get_legislation`` path always does); the parser uses it
    to synthesize ``url`` when the page lacks an ``og:url`` meta tag.
    """
    doc = _html.fromstring(html_text)

    canonical = _first_meta(doc, "og:url") or ""
    parsed_id_match = _DETAIL_ID_RE.search(canonical) if canonical else None
    resolved_id = parsed_id_match.group(1) if parsed_id_match else (legislation_id or "")

    og_title = _first_meta(doc, "og:title") or ""
    title = og_title
    jurisdiction: str | None = None
    # The og:title convention is "<Law name>, <Jurisdiction>, WIPO Lex".
    if og_title.endswith(", WIPO Lex"):
        stripped = og_title[: -len(", WIPO Lex")]
        parts = [p.strip() for p in stripped.rsplit(",", 1)]
        if len(parts) == 2:
            title, jurisdiction = parts

    summary = _first_meta(doc, "name", "description")

    files: list[WipoLexFileLink] = []
    seen_urls: set[str] = set()
    # File-link discovery: any anchor whose href contains a known doc extension.
    # The real WIPO Lex page renders the visible download buttons as custom
    # ``<wu-button class="allfileLinks">`` web components and exposes the actual
    # ``<a class="seo-only-link" href="...">`` anchors next to them, pointing at
    # ``wipolex-res.wipo.int`` with query-string cache busters. We match by
    # extension substring (the path component is reliable; the query string
    # never contains a literal ``.pdf`` token).
    selector = (
        "//a[@href and ("
        "contains(@href, '.pdf') or "
        "contains(@href, '.docx') or "
        "contains(@href, '.doc'))]"
    )
    for link in doc.xpath(selector):
        href = link.get("href") or ""
        if not href:
            continue
        url = urljoin(base_url, href)
        if url in seen_urls:
            continue
        seen_urls.add(url)
        label = " ".join((link.text_content() or "").split()).strip()
        # Strip query string before extension check (WIPO appends ?last-modified=...).
        path_only = href.split("?", 1)[0].lower()
        mime_type: str | None = None
        if path_only.endswith(".pdf"):
            mime_type = "application/pdf"
        elif path_only.endswith(".docx"):
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif path_only.endswith(".doc"):
            mime_type = "application/msword"
        files.append(
            WipoLexFileLink(
                label=label or "Attachment",
                url=url,
                mime_type=mime_type,
            )
        )

    return LegislationDetail(
        legislation_id=resolved_id,
        title=title,
        jurisdiction=jurisdiction,
        summary=summary,
        url=canonical or urljoin(base_url, f"/wipolex/en/legislation/details/{resolved_id}"),
        files=files,
    )


def _first_meta(doc, attr: str, name: str | None = None) -> str | None:
    """Read the ``content`` of the first matching ``<meta>`` tag."""
    if name is None:
        # attr is the property/name value directly (e.g. "og:title").
        nodes = doc.xpath(f"//meta[@property='{attr}']")
    else:
        nodes = doc.xpath(f"//meta[@{attr}='{name}']")
    if not nodes:
        return None
    return nodes[0].get("content") or None


__all__ = ["parse_legislation_search", "parse_legislation_detail"]
