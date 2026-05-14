"""Tests for Unitary Patent Package parsing + helper.

Parser exercise uses inline XML matching the actual EPO Register
``/rest-services/register/publication/epodoc/{n}/upp`` response shape,
captured 2026-05-14 from EP4108782.B1 (a real UP-registered patent) and
EP3666797.B1 (a granted EP that was not elected for unitary effect).
"""

from __future__ import annotations

from patent_client_agents.epo_ops.models import (
    UnitaryPatentPackage,
    UnitaryPatentStatus,
)
from patent_client_agents.epo_ops.parsing import parse_unitary_patent_package

# Excerpt from a real /upp response with unitary effect registered.
_UPP_PRESENT_XML = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ops:world-patent-data
    xmlns:ops="http://ops.epo.org"
    xmlns:reg="http://www.epo.org/register">
  <ops:register-search total-result-count="1">
    <reg:register-documents>
      <reg:register-document>
        <reg:unitary-patent>
          <reg:unitary-patent-statuses>
            <reg:unitary-patent-status change-date="20230607" status-code="9">Unitary effect registered</reg:unitary-patent-status>
            <reg:unitary-patent-status change-date="20230606" status-code="6">Request for unitary effect filed</reg:unitary-patent-status>
          </reg:unitary-patent-statuses>
        </reg:unitary-patent>
      </reg:register-document>
    </reg:register-documents>
  </ops:register-search>
</ops:world-patent-data>
"""

# Excerpt from a real /upp response WITHOUT a <reg:unitary-patent> block.
_UPP_ABSENT_XML = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ops:world-patent-data
    xmlns:ops="http://ops.epo.org"
    xmlns:reg="http://www.epo.org/register">
  <ops:register-search total-result-count="1">
    <reg:register-documents>
      <reg:register-document>
        <reg:bibliographic-data/>
      </reg:register-document>
    </reg:register-documents>
  </ops:register-search>
</ops:world-patent-data>
"""


class TestParseUnitaryPatentPackage:
    def test_returns_none_when_no_upp_block(self) -> None:
        result = parse_unitary_patent_package(_UPP_ABSENT_XML, epo_number="EP3666797.B1")
        assert result is None

    def test_extracts_status_timeline_when_present(self) -> None:
        result = parse_unitary_patent_package(_UPP_PRESENT_XML, epo_number="EP4108782.B1")
        assert result is not None
        assert isinstance(result, UnitaryPatentPackage)
        assert result.epo_number == "EP4108782.B1"
        assert len(result.statuses) == 2
        # EPO returns newest-first in the cassette
        first, second = result.statuses
        assert isinstance(first, UnitaryPatentStatus)
        assert first.status_code == "9"
        assert first.text == "Unitary effect registered"
        assert first.change_date == "20230607"
        assert second.status_code == "6"
        assert second.text == "Request for unitary effect filed"

    def test_is_registered_property(self) -> None:
        result = parse_unitary_patent_package(_UPP_PRESENT_XML, epo_number="EP4108782.B1")
        assert result is not None
        assert result.is_registered is True

    def test_is_not_registered_when_only_request_filed(self) -> None:
        # Filed but not yet granted — registered=False
        xml = _UPP_PRESENT_XML.replace(
            'change-date="20230607" status-code="9">Unitary effect registered',
            'change-date="20230607" status-code="6">Request for unitary effect filed',
        )
        result = parse_unitary_patent_package(xml, epo_number="EP4108782.B1")
        assert result is not None
        assert result.is_registered is False

    def test_latest_status_is_first(self) -> None:
        result = parse_unitary_patent_package(_UPP_PRESENT_XML, epo_number="EP4108782.B1")
        assert result is not None
        latest = result.latest_status
        assert latest is not None
        assert latest.status_code == "9"
        assert latest.change_date == "20230607"

    def test_latest_status_is_none_for_empty_statuses(self) -> None:
        upp = UnitaryPatentPackage(epo_number="EP1234567.B1", statuses=[])
        assert upp.latest_status is None
        assert upp.is_registered is False
