"""Pydantic model tests for euipo_designs."""

from __future__ import annotations

import json
from pathlib import Path

from patent_client_agents.euipo_designs import (
    Design,
    DesignSearchResult,
    Person,
    Status,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "euipo"


def test_design_search_result_parses_sandbox_listing() -> None:
    data = json.loads((FIXTURES / "design_list_size10.json").read_text())
    result = DesignSearchResult.model_validate(data)

    assert len(result.designs) == 10
    assert result.total_elements > 1_000_000  # 1.5M at capture time
    assert result.page == 0
    assert result.size == 10

    first = result.designs[0]
    # Format: NNNNNNNNN-NNNN
    assert "-" in first.design_number
    assert first.applicants  # at least one applicant required


def test_is_live_and_is_registered_for_designs() -> None:
    base = {
        "designNumber": "099999999-0001",
        "applicationDate": "2024-01-01",
        "status": "REGISTERED",
        "statusDate": "2024-02-01",
        "applicants": [{"office": "EM", "identifier": "1"}],
    }
    assert Design.model_validate(base).is_live
    assert Design.model_validate(base).is_registered

    expired = {**base, "status": "EXPIRED"}
    assert not Design.model_validate(expired).is_live

    fully_published = {**base, "status": "REGISTERED_AND_FULLY_PUBLISHED"}
    assert Design.model_validate(fully_published).is_registered

    invalid = {**base, "status": "DESIGN_DECLARED_INVALID"}
    assert not Design.model_validate(invalid).is_live


def test_person_tolerates_missing_name() -> None:
    p = Person.model_validate({"office": "EM", "identifier": "15"})
    assert p.name is None
    assert p.office == "EM"


def test_product_terms_in_helper() -> None:
    d = Design.model_validate(
        {
            "designNumber": "099999999-0002",
            "applicationDate": "2024-01-01",
            "status": "REGISTERED",
            "statusDate": "2024-02-01",
            "applicants": [{"office": "EM"}],
            "productIndications": [
                {"language": "en", "terms": ["Abdominal supports", "Sports gear"]},
                {"language": "de", "terms": ["Bauchstützen"]},
            ],
        }
    )
    assert d.product_terms_in("en") == ["Abdominal supports", "Sports gear"]
    assert d.product_terms_in("de") == ["Bauchstützen"]
    assert d.product_terms_in("xx") == []


def test_locarno_classes_round_trip() -> None:
    d = Design.model_validate(
        {
            "designNumber": "099999999-0003",
            "applicationDate": "2024-01-01",
            "status": "REGISTERED_AND_SUBJECT_TO_DEFERMENT",
            "statusDate": "2024-02-01",
            "applicants": [{"office": "EM"}],
            "locarnoClasses": ["02.01", "14.03"],
        }
    )
    assert d.locarno_classes == ["02.01", "14.03"]
    assert d.status == Status.REGISTERED_AND_SUBJECT_TO_DEFERMENT
