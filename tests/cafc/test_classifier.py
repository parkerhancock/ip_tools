"""Tests for CAFC patent case classifier."""

from patent_client_agents.cafc.classifier import PatentClassifier


class TestPatentClassifier:
    def setup_method(self):
        self.classifier = PatentClassifier()

    def test_strong_patent_case(self):
        is_patent, confidence, keywords = self.classifier.classify(
            "Apple Inc. v. Vidal, Director of the USPTO"
        )
        assert is_patent
        assert confidence >= 0.8
        assert "uspto" in keywords or "vidal" in keywords

    def test_ptab_case(self):
        is_patent, confidence, keywords = self.classifier.classify(
            "Google LLC v. Sonos, Inc. (PTAB IPR2020-01234)"
        )
        assert is_patent
        assert confidence >= 0.8

    def test_infringement_case(self):
        is_patent, confidence, keywords = self.classifier.classify(
            "Acme Corp. v. Widget Inc. - Patent Infringement"
        )
        assert is_patent
        assert "patent" in keywords

    def test_claim_construction(self):
        is_patent, confidence, keywords = self.classifier.classify(
            "In re Claim Construction of U.S. Patent No. 9,123,456"
        )
        assert is_patent

    def test_non_patent_case(self):
        is_patent, confidence, keywords = self.classifier.classify(
            "United States v. Johnson - Tax Evasion"
        )
        assert not is_patent
        assert confidence < 0.5

    def test_false_positive_patient(self):
        is_patent, confidence, _keywords = self.classifier.classify(
            "Hospital Corp. v. Insurance Co. - Patient Care Standards"
        )
        assert not is_patent

    def test_false_positive_patent_leather(self):
        is_patent, confidence, _keywords = self.classifier.classify(
            "Fashion Inc. v. Shoe Co. - Patent Leather Dispute"
        )
        assert not is_patent

    def test_statute_reference(self):
        is_patent, confidence, keywords = self.classifier.classify(
            "Obviousness under 35 U.S.C. § 103"
        )
        assert is_patent
        assert confidence >= 0.7

    def test_multiple_categories_boost(self):
        _, conf_single, _ = self.classifier.classify("patent dispute")
        _, conf_multi, _ = self.classifier.classify(
            "patent infringement under 35 U.S.C. § 101 - PTAB decision"
        )
        assert conf_multi > conf_single

    def test_empty_case_name(self):
        is_patent, confidence, keywords = self.classifier.classify("")
        assert not is_patent
        assert confidence == 0.0
        assert keywords == []

    def test_text_content_used(self):
        is_patent, confidence, keywords = self.classifier.classify(
            "Acme Corp. v. Widget Inc.",
            text_content=(
                "The PTAB issued an inter partes review decision "
                "finding claims 1-5 obvious over prior art."
            ),
        )
        assert is_patent
        assert confidence >= 0.7

    def test_pto_origin_in_name(self):
        is_patent, confidence, keywords = self.classifier.classify(
            "In re Smith - Appeal from the Patent Trial and Appeal Board"
        )
        assert is_patent


class TestClassifierEdgeCases:
    def setup_method(self):
        self.classifier = PatentClassifier()

    def test_case_insensitive(self):
        is_patent, _, _ = self.classifier.classify("USPTO PATENT INFRINGEMENT")
        assert is_patent

    def test_ipr_with_number(self):
        is_patent, _, keywords = self.classifier.classify("IPR2024-00123")
        assert is_patent
        assert any("ipr" in k for k in keywords)

    def test_section_112_reference(self):
        is_patent, _, _ = self.classifier.classify(
            "Written description requirement under Section 112"
        )
        assert is_patent
