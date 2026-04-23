"""Standardized filename helpers for download tools.

Every download tool in the MCP surface returns a ``filename`` field in its
response so agents saving files to disk use a consistent, source-native
naming convention. This module provides one formatter per source.
"""

from __future__ import annotations

import re

_UNSAFE = re.compile(r"[\\/:*?\"<>|\s]+")


def sanitize(name: str) -> str:
    """Replace filesystem-unsafe characters and whitespace with underscores."""
    cleaned = _UNSAFE.sub("_", name).strip("._")
    return cleaned or "unnamed"


# ---------------------------------------------------------------------------
# Patents
# ---------------------------------------------------------------------------


def patent_pdf(publication_number: str) -> str:
    """Google Patents convention: ``US10123456B2.pdf``."""
    normalized = sanitize(publication_number.replace("-", ""))
    return f"{normalized}.pdf"


def publication_pdf(publication_number: str) -> str:
    """USPTO PPUBS convention (hyphenated): ``US-10123456-B2.pdf``.

    Accepts either the dashed or undashed form and emits the dashed form.
    """
    raw = publication_number.strip().upper()
    if "-" in raw:
        return f"{sanitize(raw)}.pdf"
    m = re.match(r"^([A-Z]{2})(\d+)([A-Z]\d?)$", raw)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}.pdf"
    return f"{sanitize(raw)}.pdf"


def epo_pdf(publication_number: str) -> str:
    """EPO epodoc convention: ``EP1000000A1.pdf``."""
    return f"{sanitize(publication_number.replace('-', ''))}.pdf"


# ---------------------------------------------------------------------------
# USPTO ODP
# ---------------------------------------------------------------------------


def ptab_document(
    *,
    proceeding_number: str | None,
    filing_date: str | None,
    document_code: str | None,
    document_identifier: str,
) -> str:
    """PTAB document (no native convention).

    ``{proceeding}_{date}_{code}_{id}.pdf`` — components omitted when unknown.
    """
    parts = [
        sanitize(p)
        for p in (proceeding_number, filing_date, document_code, document_identifier)
        if p
    ]
    return f"{'_'.join(parts)}.pdf"


def file_history_item(
    *,
    application_number: str,
    document_code: str | None,
    mail_date: str | None,
    document_identifier: str,
    extension: str = "pdf",
) -> str:
    """USPTO ODP IFW document: ``{appl}-{code}-{date}-{id}.{ext}``."""
    parts = [
        sanitize(application_number),
        sanitize(document_code) if document_code else None,
        sanitize(mail_date) if mail_date else None,
        sanitize(document_identifier),
    ]
    stem = "-".join(p for p in parts if p)
    return f"{stem}.{extension}"


# ---------------------------------------------------------------------------
# Courts
# ---------------------------------------------------------------------------


def recap_document(
    *,
    court: str,
    pacer_case_id: str | int | None,
    document_number: str | int | None,
    attachment_number: str | int | None = 0,
    pacer_doc_id: str | None = None,
) -> str:
    """Internet Archive / RECAP convention:
    ``gov.uscourts.{court}.{pacer_case_id}.{doc_no}.{att_no}.pdf``.

    Falls back to ``gov.uscourts.{court}.{pacer_doc_id}.pdf`` when the
    case/doc/attachment triple is unavailable.
    """
    if pacer_case_id and document_number is not None:
        att = attachment_number if attachment_number is not None else 0
        return (
            f"gov.uscourts.{sanitize(court)}."
            f"{sanitize(str(pacer_case_id))}."
            f"{sanitize(str(document_number))}."
            f"{sanitize(str(att))}.pdf"
        )
    fallback = sanitize(pacer_doc_id) if pacer_doc_id else "unknown"
    return f"gov.uscourts.{sanitize(court)}.{fallback}.pdf"


def cafc_opinion(
    *,
    appeal_number: str,
    opinion_type: str | None = None,
    date: str | None = None,
    opinion_id: str | None = None,
) -> str:
    """CAFC convention: ``{appeal}.OPINION.{M-D-YYYY}_{id}.pdf``.

    ``opinion_type`` defaults to ``OPINION``; pass ``ORDER`` or
    ``NONPRECEDENTIAL`` when appropriate. If date/id are unknown, emits a
    shortened ``{appeal}.OPINION.pdf``.
    """
    kind = (opinion_type or "OPINION").upper()
    stem = f"{sanitize(appeal_number)}.{sanitize(kind)}"
    if date:
        stem += f".{sanitize(date)}"
    if opinion_id:
        stem += f"_{sanitize(opinion_id)}"
    return f"{stem}.pdf"


def scotus_opinion(docket_number: str, *, opinion_id: str | None = None) -> str:
    """SCOTUS opinion: ``{docket}_{id}.pdf`` or ``{docket}.pdf``."""
    stem = sanitize(docket_number)
    if opinion_id:
        stem += f"_{sanitize(opinion_id)}"
    return f"{stem}.pdf"


def scotus_transcript(docket_number: str, *, transcript_id: str | None = None) -> str:
    """SCOTUS argument transcript: ``{docket}_{id}.pdf``."""
    return scotus_opinion(docket_number, opinion_id=transcript_id)


def scotus_argument_audio(docket_number: str) -> str:
    """SCOTUS oral argument audio: ``{docket}.mp3``."""
    return f"{sanitize(docket_number)}.mp3"


def oral_argument_audio(audio_id: int | str, docket_number: str | None = None) -> str:
    """CourtListener oral argument audio.

    Prefers SCOTUS-style ``{docket}.mp3`` when a docket is known; otherwise
    falls back to ``cl-oralarg-{audio_id}.mp3``.
    """
    if docket_number:
        return scotus_argument_audio(docket_number)
    return f"cl-oralarg-{sanitize(str(audio_id))}.mp3"


def usitc_attachment(
    *,
    document_id: int | str,
    attachment_id: int | str,
    investigation_number: str | None = None,
    extension: str = "pdf",
) -> str:
    """USITC EDIS attachment (no native convention).

    Emits ``{inv}_{doc}_att{att}.{ext}`` when investigation is known;
    otherwise ``document-{doc}_att{att}.{ext}`` (EDIS's own stem).
    """
    doc = sanitize(str(document_id))
    att = sanitize(str(attachment_id))
    if investigation_number:
        return f"{sanitize(investigation_number)}_{doc}_att{att}.{extension}"
    return f"document-{doc}_att{att}.{extension}"


# ---------------------------------------------------------------------------
# Regulatory / financial
# ---------------------------------------------------------------------------


def sec_filing(*, accession_number: str, primary_document: str | None = None) -> str:
    """SEC EDGAR: prefer the submitted primary-document filename; fall back
    to ``{accession-no-dashes}.txt``.
    """
    if primary_document:
        return sanitize(primary_document)
    accession_nodash = accession_number.replace("-", "")
    return f"{sanitize(accession_nodash)}.txt"


def fed_reserve_letter(letter_id: str) -> str:
    """Fed Reserve SR/CA letter: ``sr2301.pdf`` / ``ca2305.pdf``.

    Accepts ``SR 23-1``, ``SR23-1``, ``SR2301``, case-insensitive. The
    number portion is zero-padded to two digits to match federalreserve.gov.
    """
    lower = letter_id.strip().lower()
    m = re.match(r"^(sr|ca)[\s-]*(\d{2})[\s-]*(\d{1,2})([a-z]\d*)?$", lower)
    if m:
        kind, yy, nn, suffix = m.groups()
        return f"{kind}{yy}{int(nn):02d}{suffix or ''}.pdf"
    compact = re.sub(r"[\s-]+", "", lower)
    return f"{sanitize(compact)}.pdf"


def occ_bulletin(bulletin_id: str) -> str:
    """OCC bulletin: ``bulletin-{yyyy}-{nn}.pdf``.

    Accepts ``OCC-2023-15``, ``OCC 2023-15``, or bare ``2023-15``.
    """
    m = re.search(r"(\d{4})[-\s]*(\d+[A-Za-z]?)", bulletin_id)
    if m:
        return f"bulletin-{m.group(1)}-{m.group(2).lower()}.pdf"
    return f"{sanitize(bulletin_id)}.pdf"
