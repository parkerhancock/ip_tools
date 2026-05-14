"""Tests for server-side date filtering in search_usitc_documents MCP tool."""

from __future__ import annotations

import pytest

from patent_client_agents.mcp.tools.usitc import _parse_edis_date
from patent_client_agents.usitc.models import EdisDocument


class TestParseEdisDate:
    """Tests for _parse_edis_date helper."""

    def test_standard_format(self) -> None:
        assert _parse_edis_date("2024-06-15 00:00:00.0") == "2024-06-15"

    def test_date_only(self) -> None:
        assert _parse_edis_date("2024-06-15") == "2024-06-15"

    def test_none(self) -> None:
        assert _parse_edis_date(None) is None

    def test_empty_string(self) -> None:
        assert _parse_edis_date("") is None

    def test_short_string(self) -> None:
        assert _parse_edis_date("2024") is None

    def test_slash_format(self) -> None:
        """EDIS production uses forward slashes: '2024/05/16 00:00:00'."""
        assert _parse_edis_date("2024/05/16 00:00:00") == "2024-05-16"

    def test_slash_date_only(self) -> None:
        assert _parse_edis_date("2024/05/16") == "2024-05-16"


class TestSearchUsitcDocumentsDateFiltering:
    """Tests for date filtering pagination logic."""

    @pytest.mark.asyncio
    async def test_date_from_filters_older_docs(self) -> None:
        """Documents before date_from should be excluded."""
        from patent_client_agents.mcp.tools.usitc import _parse_edis_date

        docs = [
            EdisDocument(id=1, **{"documentTitle": "Old", "documentDate": "2023-06-01 00:00:00.0"}),
            EdisDocument(id=2, **{"documentTitle": "New", "documentDate": "2024-06-01 00:00:00.0"}),
            EdisDocument(
                id=3, **{"documentTitle": "Newer", "documentDate": "2024-09-15 00:00:00.0"}
            ),
        ]

        date_from = "2024-01-01"
        filtered = []
        for doc in docs:
            doc_date = _parse_edis_date(doc.document_date)
            if doc_date is None:
                continue
            if date_from and doc_date < date_from:
                continue
            filtered.append(doc)

        assert len(filtered) == 2
        assert filtered[0].id == 2
        assert filtered[1].id == 3

    @pytest.mark.asyncio
    async def test_date_to_filters_newer_docs(self) -> None:
        """Documents after date_to should be excluded."""
        from patent_client_agents.mcp.tools.usitc import _parse_edis_date

        docs = [
            EdisDocument(id=1, **{"documentTitle": "Old", "documentDate": "2023-06-01 00:00:00.0"}),
            EdisDocument(id=2, **{"documentTitle": "New", "documentDate": "2024-06-01 00:00:00.0"}),
            EdisDocument(
                id=3, **{"documentTitle": "Newer", "documentDate": "2024-09-15 00:00:00.0"}
            ),
        ]

        date_to = "2024-06-30"
        filtered = []
        for doc in docs:
            doc_date = _parse_edis_date(doc.document_date)
            if doc_date is None:
                continue
            if date_to and doc_date > date_to:
                continue
            filtered.append(doc)

        assert len(filtered) == 2
        assert filtered[0].id == 1
        assert filtered[1].id == 2

    @pytest.mark.asyncio
    async def test_date_range_filters_both(self) -> None:
        """Both date_from and date_to should be applied."""
        from patent_client_agents.mcp.tools.usitc import _parse_edis_date

        docs = [
            EdisDocument(
                id=1, **{"documentTitle": "Too Old", "documentDate": "2023-06-01 00:00:00.0"}
            ),
            EdisDocument(
                id=2, **{"documentTitle": "In Range", "documentDate": "2024-03-15 00:00:00.0"}
            ),
            EdisDocument(
                id=3, **{"documentTitle": "Too New", "documentDate": "2024-09-15 00:00:00.0"}
            ),
        ]

        date_from = "2024-01-01"
        date_to = "2024-06-30"
        filtered = []
        for doc in docs:
            doc_date = _parse_edis_date(doc.document_date)
            if doc_date is None:
                continue
            if date_from and doc_date < date_from:
                continue
            if date_to and doc_date > date_to:
                continue
            filtered.append(doc)

        assert len(filtered) == 1
        assert filtered[0].id == 2

    @pytest.mark.asyncio
    async def test_null_dates_excluded(self) -> None:
        """Documents with no document_date should be excluded when filtering."""
        from patent_client_agents.mcp.tools.usitc import _parse_edis_date

        docs = [
            EdisDocument(id=1, **{"documentTitle": "No Date"}),
            EdisDocument(
                id=2, **{"documentTitle": "Has Date", "documentDate": "2024-06-01 00:00:00.0"}
            ),
        ]

        date_from = "2024-01-01"
        filtered = []
        for doc in docs:
            doc_date = _parse_edis_date(doc.document_date)
            if doc_date is None:
                continue
            if date_from and doc_date < date_from:
                continue
            filtered.append(doc)

        assert len(filtered) == 1
        assert filtered[0].id == 2

    @pytest.mark.asyncio
    async def test_boundary_dates_inclusive(self) -> None:
        """date_from and date_to should be inclusive."""
        from patent_client_agents.mcp.tools.usitc import _parse_edis_date

        docs = [
            EdisDocument(
                id=1, **{"documentTitle": "Start", "documentDate": "2024-01-01 00:00:00.0"}
            ),
            EdisDocument(id=2, **{"documentTitle": "End", "documentDate": "2024-12-31 00:00:00.0"}),
        ]

        date_from = "2024-01-01"
        date_to = "2024-12-31"
        filtered = []
        for doc in docs:
            doc_date = _parse_edis_date(doc.document_date)
            if doc_date is None:
                continue
            if date_from and doc_date < date_from:
                continue
            if date_to and doc_date > date_to:
                continue
            filtered.append(doc)

        assert len(filtered) == 2
