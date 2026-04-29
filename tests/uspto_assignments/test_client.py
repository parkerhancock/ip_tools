"""Tests for USPTO Assignment Center client."""

from __future__ import annotations

import pytest

from patent_client_agents.uspto_assignments import (
    ApplicationAssignmentBundle,
    AssignmentCenterClient,
    AssignmentDetail,
    AssignmentRecord,
    Assignor,
    Property,
)


class TestModels:
    """Tests for Pydantic models."""

    def test_assignor_model(self) -> None:
        """Test Assignor model parsing."""
        data = {"assignorName": "SMITH, JOHN", "executionDate": "01/15/2024"}
        assignor = Assignor.model_validate(data)
        assert assignor.assignor_name == "SMITH, JOHN"
        assert assignor.execution_date == "01/15/2024"

    def test_property_model(self) -> None:
        """Test Property model parsing."""
        data = {
            "sequenceNumber": 1,
            "applicationNumber": "17123456",
            "fillingDate": "01/01/2024",  # Note: API typo
            "patentNumber": "11000000",
            "inventionTitle": "Test Invention",
            "inventors": "John Smith, Jane Doe",
        }
        prop = Property.model_validate(data)
        assert prop.application_number == "17123456"
        assert prop.patent_number == "11000000"
        assert prop.invention_title == "Test Invention"

    def test_assignment_record_model(self) -> None:
        """Test AssignmentRecord model parsing."""
        data = {
            "reelNumber": 52614,
            "frameNumber": 446,
            "assignorExecutionDate": "04/29/2020",
            "correspondentName": "LAW FIRM LLC",
            "assignors": [{"assignorName": "INVENTOR", "executionDate": "04/29/2020"}],
            "assignees": ["COMPANY INC."],
            "noOfProperties": 1,
            "properties": [{"sequenceNumber": 1, "applicationNumber": "17123456"}],
        }
        record = AssignmentRecord.model_validate(data)
        assert record.reel_number == 52614
        assert record.frame_number == 446
        assert record.reel_frame == "52614/446"
        assert len(record.assignors) == 1
        assert record.assignors[0].assignor_name == "INVENTOR"
        assert record.assignees == ["COMPANY INC."]
        assert record.number_of_properties == 1

    def test_assignment_detail_model(self) -> None:
        """Test AssignmentDetail model parsing (search/patent endpoint shape)."""
        data = {
            "reelNumber": 58293,
            "frameNumber": 75,
            "conveyance": "CHANGE OF NAME",
            "conveyanceCode": 33,
            "recordationDate": "12/01/2021",
            "receiptDate": "12/01/2021",
            "mailDate": "12/08/2021",
            "pageCount": 5,
            "imageURL": "https://assignmentcenter.uspto.gov/.../58293/75",
            "assignors": [{"assignorName": "LATCH, INC.", "executionDate": "06/01/2021"}],
            "assignees": [{"assigneeName": "LATCH SYSTEMS, INC."}],
        }
        detail = AssignmentDetail.model_validate(data)
        assert detail.reel_number == 58293
        assert detail.frame_number == 75
        assert detail.reel_frame == "58293/75"
        assert detail.conveyance == "CHANGE OF NAME"
        assert detail.conveyance_code == 33
        assert detail.recordation_date == "12/01/2021"
        assert detail.assignors[0].assignor_name == "LATCH, INC."

    def test_application_assignment_bundle_model(self) -> None:
        """Test ApplicationAssignmentBundle model parsing."""
        data = {
            "properties": {"applicationNumber": "16136935", "patentNumber": "10872483"},
            "noOfAssignments": 2,
            "assignment": [
                {
                    "reelNumber": 58293,
                    "frameNumber": 75,
                    "conveyance": "CHANGE OF NAME",
                    "conveyanceCode": 33,
                },
                {
                    "reelNumber": 47386,
                    "frameNumber": 595,
                    "conveyance": "ASSIGNMENT OF ASSIGNOR'S INTEREST",
                    "conveyanceCode": 23,
                },
            ],
        }
        bundle = ApplicationAssignmentBundle.model_validate(data)
        assert bundle.no_of_assignments == 2
        assert len(bundle.assignment) == 2
        assert bundle.assignment[0].conveyance == "CHANGE OF NAME"
        assert bundle.assignment[1].conveyance == "ASSIGNMENT OF ASSIGNOR'S INTEREST"


class TestClient:
    """Tests for AssignmentCenterClient using VCR cassettes.

    To record new cassettes:
        pytest tests/uspto_assignments/ --vcr-record=once -v
    """

    @pytest.mark.asyncio
    async def test_search_by_assignee(self, vcr_cassette) -> None:
        """Test searching by assignee name."""
        async with AssignmentCenterClient() as client:
            records = await client.search_by_assignee("Apple Inc", limit=5)
            assert len(records) > 0
            assert all(isinstance(r, AssignmentRecord) for r in records)
            # All results should have Apple as an assignee
            for record in records:
                assignee_names = [a.lower() for a in record.assignees]
                assert any("apple" in name for name in assignee_names)

    @pytest.mark.asyncio
    async def test_search_by_assignor(self, vcr_cassette) -> None:
        """Test searching by assignor name."""
        async with AssignmentCenterClient() as client:
            records = await client.search_by_assignor("Samsung", limit=5)
            assert len(records) > 0
            assert all(isinstance(r, AssignmentRecord) for r in records)

    @pytest.mark.asyncio
    async def test_search_by_patent(self, vcr_cassette) -> None:
        """Test searching by patent number."""
        async with AssignmentCenterClient() as client:
            records = await client.search_by_patent("10000000")
            assert len(records) > 0
            # Should find assignments for patent 10,000,000
            for record in records:
                patent_numbers = [
                    p.patent_number.strip() if p.patent_number else "" for p in record.properties
                ]
                assert any("10000000" in pn for pn in patent_numbers)

    @pytest.mark.asyncio
    async def test_search_by_application(self, vcr_cassette) -> None:
        """Test searching by application number."""
        async with AssignmentCenterClient() as client:
            # Application for patent 10,000,000
            records = await client.search_by_application("14643719")
            assert len(records) > 0
            assert all(isinstance(r, AssignmentRecord) for r in records)

    @pytest.mark.asyncio
    async def test_search_by_reel_frame(self, vcr_cassette) -> None:
        """Test searching by reel/frame."""
        async with AssignmentCenterClient() as client:
            # Known reel/frame from patent 10,000,000
            records = await client.search_by_reel_frame("37879/527")
            assert len(records) > 0
            assert records[0].reel_frame == "37879/527"

    @pytest.mark.asyncio
    async def test_search_multi_criteria(self, vcr_cassette) -> None:
        """Test searching with multiple criteria."""
        async with AssignmentCenterClient() as client:
            records = await client.search(
                assignee_name="Apple",
                limit=5,
            )
            assert len(records) > 0

    @pytest.mark.asyncio
    async def test_get_application_assignments(self, vcr_cassette) -> None:
        """Test fetching per-application assignment detail with conveyance type."""
        async with AssignmentCenterClient() as client:
            # Application 16136935 has three recordations, two of which are
            # CHANGE OF NAME and one ASSIGNMENT OF ASSIGNOR'S INTEREST.
            bundle = await client.get_application_assignments("16136935")
            assert bundle.no_of_assignments >= 1
            assert len(bundle.assignment) >= 1
            # Conveyance type must be populated by this endpoint.
            for asgn in bundle.assignment:
                assert asgn.conveyance is not None
                assert asgn.conveyance != ""

    @pytest.mark.asyncio
    async def test_search_requires_criteria(self) -> None:
        """Test that search() requires at least one criterion."""
        async with AssignmentCenterClient() as client:
            with pytest.raises(ValueError, match="At least one search criterion"):
                await client.search()
