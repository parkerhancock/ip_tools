"""Parser tests for ``patent_client_agents.upc_decisions``.

Uses inline HTML fixtures rather than VCR cassettes:

1. The UPC site is a Drupal Views table — the parser only depends on
   the stable cell-headers pattern. Pinning that contract to inline
   fixtures is more explicit than checking in 500KB of live HTML.
2. The listing changes daily as new orders are filed, so VCR cassettes
   would go stale within hours of recording.

When UPC restyles the page, update these fixtures and the
``client.py`` selectors together.
"""

from __future__ import annotations

import pytest

from patent_client_agents.upc_decisions.client import (
    DEFAULT_BASE_URL,
    _canonicalize_case_id,
    parse_decisions_page,
)

# Minimal fixture covering the four cell variants the parser supports:
# CFI underscored, CFI hyphenated, CoA mixed-case, ACT registry number.
FIXTURE_LISTING = """<!DOCTYPE html><html><body>
<table>
  <thead>
    <tr>
      <th id="view-field-judgement-application-no-1-table-column">Case</th>
      <th id="view-field-location-table-column">Court</th>
      <th id="view-field-upc-case-type-table-column">Type</th>
      <th id="view-field-judgement-parties-long-table-column">Parties</th>
      <th id="view-field-upc-document-table-column">Document</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td headers="view-field-judgement-application-no-1-table-column">
        UPC_CFI_1747/2025<br/>UPC_CFI_1747/2025<br/>
        <a href="/en/node/183235" class="btn btn--compact btn--primary">Full Details</a>
      </td>
      <td headers="view-field-location-table-column">Düsseldorf (DE) Local Division</td>
      <td headers="view-field-upc-case-type-table-column">Application for provisional measures</td>
      <td headers="view-field-judgement-parties-long-table-column">Align Technology, Inc. <br/>v.<br/>Angelalign France Technology SASU a. o.</td>
      <td headers="view-field-upc-document-table-column">
        <div class="item-list"><ul><li><article class="media media--type-cms-api-document">
          <a href="/sites/default/files/files/api_order/Final%20Order_UPC_CFI_1747_2025.pdf">Final Order</a>
        </article></li></ul></div>
      </td>
    </tr>
    <tr>
      <td headers="view-field-judgement-application-no-1-table-column">
        UPC-CFI-478/2025<br/>UPC-CFI-478/2025<br/>
        <a href="/en/node/183250" class="btn btn--compact btn--primary">Full Details</a>
      </td>
      <td headers="view-field-location-table-column">The Hague (NL) Local Division</td>
      <td headers="view-field-upc-case-type-table-column">Infringement Action</td>
      <td headers="view-field-judgement-parties-long-table-column">Avient Protective Materials B.V. <br/>v.<br/>Xingi Technology Co., Ltd et al</td>
      <td headers="view-field-upc-document-table-column">
        <a href="/sites/default/files/files/api_order/CFI-478-2025-decision.pdf">Decision</a>
      </td>
    </tr>
    <tr>
      <td headers="view-field-judgement-application-no-1-table-column">
        UPC-COA-0000053/2026<br/>UPC-COA-0000053/2026<br/>
        <a href="/en/node/183265" class="btn btn--compact btn--primary">Full Details</a>
      </td>
      <td headers="view-field-location-table-column">Luxembourg (LU)</td>
      <td headers="view-field-upc-case-type-table-column">Request for a discretionary review (RoP 220.3)</td>
      <td headers="view-field-judgement-parties-long-table-column">Huawei Technologies Co. Ltd. <br/>v.<br/>Quinn Emanuel Urquhart &amp; Sullivan, LLP</td>
      <td headers="view-field-upc-document-table-column">
        <a href="https://www.unifiedpatentcourt.org/sites/default/files/files/api_order/CoA-53-2026.pdf">Order</a>
      </td>
    </tr>
    <tr>
      <td headers="view-field-judgement-application-no-1-table-column">
        ACT_551054/2023<br/>UPC_CFI_159/2023<br/>
        <a href="/en/node/100001" class="btn btn--compact btn--primary">Full Details</a>
      </td>
      <td headers="view-field-location-table-column">Stockholm (SE) - Seat of the Regional Division</td>
      <td headers="view-field-upc-case-type-table-column">Infringement Action</td>
      <td headers="view-field-judgement-parties-long-table-column">Edwards Lifesciences Corporation<br/>v.<br/>Meril Life Sciences Pvt Limited</td>
      <td headers="view-field-upc-document-table-column">
        <a href="/sites/default/files/files/api_order/551054-2023%20Final%20order.pdf">Final order</a>
      </td>
    </tr>
  </tbody>
</table>

<nav class="pager">
  <ul class="pager__items js-pager__items">
    <li class="pager__item is-active"><a href="?page=0">1</a></li>
    <li class="pager__item"><a href="?page=1">2</a></li>
    <li class="pager__item pager__item--last">
      <a href="?page=37">Last page</a>
    </li>
  </ul>
</nav>

<select name="proceedings_lang">
  <option value="All">All</option>
  <option value="33">English</option>
  <option value="34">French</option>
  <option value="35">German</option>
</select>
<select name="division_1">
  <option value="All">All</option>
  <option value="125">Luxembourg (LU)</option>
  <option value="134">Düsseldorf (DE) Local Division</option>
</select>
</body></html>"""


def test_parse_decisions_recovers_all_rows():
    rows, total_pages = parse_decisions_page(FIXTURE_LISTING)
    assert len(rows) == 4
    assert total_pages == 38  # last-page index 37 → 38 total


def test_canonicalize_case_ids_normalizes_variants():
    # Underscores stay; hyphens flip to underscores; CoA mixed-case is
    # preserved; ACT_ stays ACT_.
    rows, _ = parse_decisions_page(FIXTURE_LISTING)
    case_ids = [r.case_id for r in rows]
    assert case_ids == [
        "UPC_CFI_1747/2025",
        "UPC_CFI_478/2025",
        "UPC_CoA_0000053/2026",
        "ACT_551054/2023",
    ]


def test_canonicalize_case_id_helper_variants():
    assert _canonicalize_case_id("UPC-COA-35/2026") == "UPC_CoA_35/2026"
    assert _canonicalize_case_id("UPC_CFI_0001695/2025") == "UPC_CFI_0001695/2025"
    assert _canonicalize_case_id("ACT_12345/2024") == "ACT_12345/2024"
    # Unrecognized strings come back unchanged so callers can spot drift.
    assert _canonicalize_case_id("not-a-case-id") == "not-a-case-id"


def test_pdf_urls_resolved_against_base():
    rows, _ = parse_decisions_page(FIXTURE_LISTING)
    pdf_urls = [r.pdf_urls[0] for r in rows]
    assert pdf_urls[0].startswith(f"{DEFAULT_BASE_URL}/sites/default/files/files/api_order/")
    # Absolute URL in fixture is passed through verbatim.
    assert (
        pdf_urls[2]
        == "https://www.unifiedpatentcourt.org/sites/default/files/files/api_order/CoA-53-2026.pdf"
    )


def test_parties_split_on_v_separator():
    rows, _ = parse_decisions_page(FIXTURE_LISTING)
    huawei_row = rows[2]
    assert huawei_row.parties == [
        "Huawei Technologies Co. Ltd.",
        "Quinn Emanuel Urquhart & Sullivan, LLP",
    ]


def test_detail_url_absolute():
    rows, _ = parse_decisions_page(FIXTURE_LISTING)
    assert rows[0].detail_url == f"{DEFAULT_BASE_URL}/en/node/183235"


def test_court_and_type_extracted():
    rows, _ = parse_decisions_page(FIXTURE_LISTING)
    assert rows[0].court == "Düsseldorf (DE) Local Division"
    assert rows[0].type_of_action == "Application for provisional measures"


def test_empty_table_returns_empty_list():
    empty = "<html><body><table><tbody></tbody></table></body></html>"
    rows, total_pages = parse_decisions_page(empty)
    assert rows == []
    assert total_pages == 1  # no pager rendered → single-page fallback


def test_invalid_language_rejected_at_client_init():
    from patent_client_agents.upc_decisions import UpcDecisionsClient

    with pytest.raises(ValueError, match="language must be"):
        UpcDecisionsClient(language="xx")
