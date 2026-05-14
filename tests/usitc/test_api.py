from __future__ import annotations

from typing import Any, cast

import pytest
from pydantic import AnyHttpUrl

from patent_client_agents.usitc import api as usitc_api
from patent_client_agents.usitc.models import (
    DataWebReport,
    DownloadedAttachment,
    EdisAttachment,
    EdisDocument,
    EdisInvestigation,
    HtsExportResponse,
    HtsSearchResult,
    IdsInvestigation,
    SavedQuerySummary,
)


@pytest.mark.asyncio
async def test_edis_search_investigations() -> None:
    class DummyClient:
        async def list_investigations(
            self,
            investigation_number: str | None = None,
            investigation_phase: str | None = None,
            **kwargs: object,
        ) -> list[EdisInvestigation]:
            assert investigation_number == "1234"
            return [EdisInvestigation(investigationNumber="1234")]

    result = await usitc_api.edis_search_investigations(
        investigation_number="1234", client=cast(Any, DummyClient())
    )
    assert result[0].investigation_number == "1234"


@pytest.mark.asyncio
async def test_edis_list_documents() -> None:
    class DummyClient:
        async def list_documents(self, **kwargs: object) -> list[EdisDocument]:
            assert kwargs["investigationNumber"] is None
            return [EdisDocument(id=1, investigationNumber="1234")]

    result = await usitc_api.edis_list_documents(client=cast(Any, DummyClient()))
    assert result[0].id == 1


@pytest.mark.asyncio
async def test_edis_list_attachments() -> None:
    class DummyClient:
        async def list_attachments(self, document_id: int) -> list[EdisAttachment]:
            assert document_id == 11
            return [
                EdisAttachment(
                    id=1,
                    documentId=document_id,
                    downloadUri=cast(AnyHttpUrl, "https://example.com/file"),
                )
            ]

    result = await usitc_api.edis_list_attachments(11, client=cast(Any, DummyClient()))
    assert result[0].document_id == 11


@pytest.mark.asyncio
async def test_edis_download_attachment() -> None:
    class DummyClient:
        async def download_attachment(
            self, document_id: int, attachment_id: int
        ) -> DownloadedAttachment:
            assert document_id == 11
            assert attachment_id == 22
            return DownloadedAttachment(
                document_id=document_id,
                attachment_id=attachment_id,
                filename="file.pdf",
                content_type="application/pdf",
                content_base64="ZGF0YQ==",
            )

    result = await usitc_api.edis_download_attachment(
        document_id=11,
        attachment_id=22,
        client=cast(Any, DummyClient()),
    )
    assert result.filename == "file.pdf"


@pytest.mark.asyncio
async def test_dataweb_run_report() -> None:
    class DummyClient:
        async def run_report(self, query: dict[str, Any]) -> DataWebReport:
            assert query == {"foo": "bar"}
            return DataWebReport(dto={}, raw={})

    result = await usitc_api.dataweb_run_report({"foo": "bar"}, client=cast(Any, DummyClient()))
    assert isinstance(result, DataWebReport)


@pytest.mark.asyncio
async def test_dataweb_list_saved_queries() -> None:
    class DummyClient:
        async def list_saved_queries(self) -> list[SavedQuerySummary]:
            return [SavedQuerySummary(id=1, name="demo")]

    result = await usitc_api.dataweb_list_saved_queries(client=cast(Any, DummyClient()))
    assert result[0].name == "demo"


@pytest.mark.asyncio
async def test_ids_list_investigations() -> None:
    class DummyClient:
        async def list_investigations(self) -> list[IdsInvestigation]:
            return [
                IdsInvestigation(
                    **{
                        "Investigation ID": 1,
                        "Investigation Number": "1234",
                        "Product Group Code Description": "Group",
                        "Phase Number": "Phase",
                        "Docket Number": "Docket",
                        "Staff": [],
                        "Participants": [],
                    }
                )
            ]

    result = await usitc_api.ids_list_investigations(client=cast(Any, DummyClient()))
    assert result[0].investigation_id == 1


@pytest.mark.asyncio
async def test_hts_search() -> None:
    class DummyClient:
        async def search(self, keyword: str) -> list[HtsSearchResult]:
            assert keyword == "steel"
            return [HtsSearchResult(htsno="1234.56", description="Test")]

    result = await usitc_api.hts_search("steel", client=cast(Any, DummyClient()))
    assert result[0].hts_number == "1234.56"


@pytest.mark.asyncio
async def test_hts_export_range() -> None:
    class DummyClient:
        async def export_range(
            self, from_code: str, to_code: str, format_: str, styles: bool
        ) -> HtsExportResponse:
            assert from_code == "0101.10"
            assert to_code == "0101.90"
            assert format_ == "JSON"
            assert styles is True
            return HtsExportResponse(entries=[], raw=[])

    result = await usitc_api.hts_export_range(
        "0101.10",
        "0101.90",
        client=cast(Any, DummyClient()),
    )
    assert isinstance(result, HtsExportResponse)
