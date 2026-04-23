"""Tests for law_tools_core/filenames.py."""

from __future__ import annotations

from law_tools_core import filenames as fn


class TestSanitize:
    def test_replaces_unsafe_chars(self) -> None:
        assert fn.sanitize("a/b c:d") == "a_b_c_d"

    def test_strips_dots_underscores(self) -> None:
        assert fn.sanitize("..foo..") == "foo"

    def test_empty_falls_back(self) -> None:
        assert fn.sanitize("///") == "unnamed"


class TestPatents:
    def test_patent_pdf_strips_dashes(self) -> None:
        assert fn.patent_pdf("US-10123456-B2") == "US10123456B2.pdf"

    def test_publication_pdf_adds_dashes(self) -> None:
        assert fn.publication_pdf("US10123456B2") == "US-10123456-B2.pdf"

    def test_publication_pdf_preserves_dashed(self) -> None:
        assert fn.publication_pdf("US-20230012345-A1") == "US-20230012345-A1.pdf"

    def test_epo_pdf(self) -> None:
        assert fn.epo_pdf("EP-1000000-A1") == "EP1000000A1.pdf"


class TestRecap:
    def test_full_tuple(self) -> None:
        assert (
            fn.recap_document(
                court="cand",
                pacer_case_id="252324",
                document_number=1,
                attachment_number=0,
            )
            == "gov.uscourts.cand.252324.1.0.pdf"
        )

    def test_fallback_to_doc_id(self) -> None:
        assert (
            fn.recap_document(
                court="cand", pacer_case_id=None, document_number=None, pacer_doc_id="abc123"
            )
            == "gov.uscourts.cand.abc123.pdf"
        )


class TestCAFC:
    def test_full(self) -> None:
        assert (
            fn.cafc_opinion(appeal_number="22-1822", date="10-3-2023", opinion_id="2202843")
            == "22-1822.OPINION.10-3-2023_2202843.pdf"
        )

    def test_nonprecedential(self) -> None:
        assert (
            fn.cafc_opinion(appeal_number="22-1", opinion_type="NONPRECEDENTIAL")
            == "22-1.NONPRECEDENTIAL.pdf"
        )


class TestScotus:
    def test_opinion(self) -> None:
        assert fn.scotus_opinion("22-451", opinion_id="i426") == "22-451_i426.pdf"

    def test_audio(self) -> None:
        assert fn.scotus_argument_audio("22-451") == "22-451.mp3"

    def test_oa_fallback(self) -> None:
        assert fn.oral_argument_audio(12345) == "cl-oralarg-12345.mp3"

    def test_oa_with_docket(self) -> None:
        assert fn.oral_argument_audio(12345, docket_number="22-451") == "22-451.mp3"


class TestUspto:
    def test_ptab(self) -> None:
        assert (
            fn.ptab_document(
                proceeding_number="IPR2020-00123",
                filing_date="2020-01-15",
                document_code="PET",
                document_identifier="abc",
            )
            == "IPR2020-00123_2020-01-15_PET_abc.pdf"
        )

    def test_ptab_partial(self) -> None:
        assert (
            fn.ptab_document(
                proceeding_number=None,
                filing_date=None,
                document_code=None,
                document_identifier="abc",
            )
            == "abc.pdf"
        )

    def test_file_history(self) -> None:
        assert (
            fn.file_history_item(
                application_number="16123456",
                document_code="CTNF",
                mail_date="2023-01-15",
                document_identifier="XYZ",
            )
            == "16123456-CTNF-2023-01-15-XYZ.pdf"
        )


class TestRegulatory:
    def test_sec_primary_doc(self) -> None:
        assert (
            fn.sec_filing(accession_number="0001193125-23-045678", primary_document="d123d10k.htm")
            == "d123d10k.htm"
        )

    def test_sec_fallback(self) -> None:
        assert fn.sec_filing(accession_number="0001193125-23-045678") == "000119312523045678.txt"

    def test_fed_letter(self) -> None:
        assert fn.fed_reserve_letter("SR 23-1") == "sr2301.pdf"
        assert fn.fed_reserve_letter("SR2301") == "sr2301.pdf"

    def test_occ_bulletin(self) -> None:
        assert fn.occ_bulletin("OCC-2023-15") == "bulletin-2023-15.pdf"
        assert fn.occ_bulletin("2023-15") == "bulletin-2023-15.pdf"


class TestUsitc:
    def test_no_investigation(self) -> None:
        assert (
            fn.usitc_attachment(document_id=123, attachment_id=4, extension="pdf")
            == "document-123_att4.pdf"
        )

    def test_with_investigation(self) -> None:
        assert (
            fn.usitc_attachment(
                document_id=123, attachment_id=4, investigation_number="337-TA-1234"
            )
            == "337-TA-1234_123_att4.pdf"
        )
