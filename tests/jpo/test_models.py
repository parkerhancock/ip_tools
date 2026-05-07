"""Tests for JPO models — built from real production payloads (2026-05-07)."""

from __future__ import annotations

from patent_client_agents.jpo.models import (
    EMPTY_STATUS_CODES,
    ApiResult,
    ApplicantAttorney,
    ApplicantAttorneyClass,
    BibliographyDocument,
    BibliographyInformation,
    CaseNumberKind,
    CitedDocumentsData,
    DesignProgressData,
    DivisionalAppInfoData,
    DivisionalApplicationInfo,
    DocumentBundleResult,
    DocumentSeparator,
    DocumentType,
    GoodsServiceInformation,
    NonPatentCitedDocument,
    NumberReference,
    NumberType,
    ParentApplicationInfo,
    PatentCitedDocument,
    PatentProgressData,
    PctKind,
    PctNationalPhaseData,
    PriorityInfo,
    RegistrationInfo,
    RightPersonInfo,
    SimplifiedPatentProgressData,
    StatusCode,
    TrademarkProgressData,
)

# =============================================================================
# Enum tests
# =============================================================================


class TestStatusCode:
    def test_success_value(self) -> None:
        assert StatusCode.SUCCESS.value == "100"

    def test_no_data_value(self) -> None:
        assert StatusCode.NO_DATA.value == "107"

    def test_no_document_value(self) -> None:
        assert StatusCode.NO_DOCUMENT.value == "108"

    def test_unavailable_number_value(self) -> None:
        assert StatusCode.UNAVAILABLE_NUMBER.value == "111"

    def test_daily_limit_value(self) -> None:
        assert StatusCode.DAILY_LIMIT_EXCEEDED.value == "203"

    def test_invalid_token_value(self) -> None:
        assert StatusCode.INVALID_TOKEN.value == "210"

    def test_concentrated_access_value(self) -> None:
        assert StatusCode.CONCENTRATED_ACCESS.value == "303"

    def test_all_codes_are_strings(self) -> None:
        for code in StatusCode:
            assert isinstance(code.value, str)

    def test_empty_status_codes_includes_111(self) -> None:
        assert StatusCode.UNAVAILABLE_NUMBER.value in EMPTY_STATUS_CODES
        assert StatusCode.NO_DATA.value in EMPTY_STATUS_CODES
        assert StatusCode.NO_DOCUMENT.value in EMPTY_STATUS_CODES


class TestNumberType:
    """The numeric numberType codes used inside bibliographyInformation."""

    def test_application_value(self) -> None:
        assert NumberType.APPLICATION.value == "01"

    def test_publication_value(self) -> None:
        assert NumberType.PUBLICATION.value == "02"

    def test_registration_value(self) -> None:
        assert NumberType.REGISTRATION.value == "06"

    def test_pct_application_value(self) -> None:
        assert NumberType.PCT_APPLICATION.value == "10"


class TestCaseNumberKind:
    def test_application_value(self) -> None:
        assert CaseNumberKind.APPLICATION.value == "application"

    def test_publication_value(self) -> None:
        assert CaseNumberKind.PUBLICATION.value == "publication"

    def test_registration_value(self) -> None:
        assert CaseNumberKind.REGISTRATION.value == "registration"


class TestPctKind:
    def test_international_application_value(self) -> None:
        assert PctKind.INTERNATIONAL_APPLICATION.value == "international_application"

    def test_international_publication_value(self) -> None:
        assert PctKind.INTERNATIONAL_PUBLICATION.value == "international_publication"


class TestApplicantAttorneyClass:
    def test_applicant_value(self) -> None:
        assert ApplicantAttorneyClass.APPLICANT.value == "1"

    def test_attorney_value(self) -> None:
        assert ApplicantAttorneyClass.ATTORNEY.value == "2"


class TestDocumentSeparator:
    def test_biblio_value(self) -> None:
        assert DocumentSeparator.BIBLIO.value == "S"

    def test_claims_value(self) -> None:
        assert DocumentSeparator.CLAIMS.value == "L"

    def test_drawings_value(self) -> None:
        assert DocumentSeparator.DRAWINGS.value == "Z"

    def test_document_type_alias(self) -> None:
        # DocumentType retained as a backwards-compat alias.
        assert DocumentType is DocumentSeparator


# =============================================================================
# ApiResult
# =============================================================================


class TestApiResult:
    def test_creates_from_alias(self) -> None:
        result = ApiResult(
            statusCode="100",
            errorMessage="",
            remainAccessCount="50",
            data={"key": "value"},
        )
        assert result.status_code == "100"
        assert result.remain_access_count == "50"

    def test_creates_from_field_name(self) -> None:
        result = ApiResult.model_validate(
            {
                "statusCode": "100",
                "errorMessage": "",
                "remainAccessCount": "50",
            }
        )
        assert result.status_code == "100"

    def test_is_success_true(self) -> None:
        assert ApiResult(statusCode="100").is_success is True

    def test_is_success_false(self) -> None:
        assert ApiResult(statusCode="107").is_success is False

    def test_has_data_true(self) -> None:
        assert ApiResult(statusCode="100").has_data is True

    def test_has_data_false_no_data(self) -> None:
        assert ApiResult(statusCode="107").has_data is False

    def test_has_data_false_no_document(self) -> None:
        assert ApiResult(statusCode="108").has_data is False

    def test_has_data_false_unavailable_number(self) -> None:
        # 111 (out of scope) is treated as "no data" so callers don't need
        # to special-case it.
        assert ApiResult(statusCode="111").has_data is False

    def test_defaults(self) -> None:
        result = ApiResult(statusCode="100")
        assert result.error_message == ""
        assert result.remain_access_count == ""
        assert result.data is None


# =============================================================================
# Component models
# =============================================================================


class TestApplicantAttorney:
    def test_creates_from_alias(self) -> None:
        applicant = ApplicantAttorney(
            applicantAttorneyCd="123456789",
            repeatNumber="01",
            name="Test Company",
            applicantAttorneyClass="1",
        )
        assert applicant.applicant_attorney_cd == "123456789"
        assert applicant.name == "Test Company"

    def test_defaults(self) -> None:
        applicant = ApplicantAttorney()
        assert applicant.applicant_attorney_cd == ""
        assert applicant.name == ""


class TestPriorityInfo:
    """PriorityInfo now mirrors the live priorityRightInformation rows."""

    def test_paris_priority(self) -> None:
        priority = PriorityInfo(
            parisPriorityApplicationNumber="US63/123456",
            parisPriorityDate="20200115",
            parisPriorityCountryCd="US",
        )
        assert priority.paris_priority_application_number == "US63/123456"
        assert priority.paris_priority_country_cd == "US"

    def test_national_priority(self) -> None:
        priority = PriorityInfo.model_validate(
            {
                "nationalPriorityLawCd": "1",
                "nationalPriorityApplicationNumber": "2019210418",
                "nationalPriorityDate": "20191121",
            }
        )
        assert priority.national_priority_law_cd == "1"
        assert priority.national_priority_application_number == "2019210418"
        assert priority.national_priority_date == "20191121"

    def test_defaults_blank(self) -> None:
        priority = PriorityInfo()
        assert priority.paris_priority_application_number == ""
        assert priority.national_priority_application_number == ""


class TestParentApplicationInfo:
    def test_full(self) -> None:
        parent = ParentApplicationInfo(
            parentApplicationNumber="2018005678",
            filingDate="20180101",
            parentApplicationCategory="01",
            parentApplicationLawCode="1",
        )
        assert parent.parent_application_number == "2018005678"
        assert parent.filing_date == "20180101"


class TestDivisionalApplicationInfo:
    def test_full_row(self) -> None:
        div = DivisionalApplicationInfo.model_validate(
            {
                "applicationNumber": "2021100000",
                "publicationNumber": "JP-2022-1",
                "ADPublicationNumber": "2022-001",
                "registrationNumber": "7000001",
                "divisionalGeneration": "1",
                "erasureIdentifier": "00",
            }
        )
        assert div.application_number == "2021100000"
        assert div.divisional_generation == "1"
        assert div.ad_publication_number == "2022-001"


class TestBibliographyInformation:
    def test_with_documents(self) -> None:
        bib = BibliographyInformation.model_validate(
            {
                "numberType": "01",
                "number": "2020123456",
                "documentList": [
                    {
                        "legalDate": "20200720",
                        "irirFlg": "0",
                        "availabilityFlag": "1",
                        "documentCode": "A63",
                        "documentDescription": "要約書",
                        "documentNumber": "52001475960",
                        "versionNumber": "0001",
                        "documentSeparator": "Y",
                        "numberOfPages": "0",
                        "sizeOfDocument": "1208",
                    },
                ],
            }
        )
        assert bib.number_type == "01"
        assert len(bib.document_list) == 1
        assert bib.document_list[0].document_description == "要約書"
        assert isinstance(bib.document_list[0], BibliographyDocument)


class TestRightPersonInfo:
    def test_basic(self) -> None:
        rp = RightPersonInfo(rightPersonCd="000114400", rightPersonName="Test Co")
        assert rp.right_person_cd == "000114400"
        assert rp.right_person_name == "Test Co"


class TestGoodsServiceInformation:
    def test_basic(self) -> None:
        gs = GoodsServiceInformation(
            goodsServiceClass="36",
            goodsServiceName="建物の管理",
            similarCode="36D01",
        )
        assert gs.goods_service_class == "36"
        assert gs.similar_code == "36D01"


# =============================================================================
# Patent progress
# =============================================================================


class TestPatentProgressData:
    def test_creates_full_model(self) -> None:
        data = PatentProgressData(
            applicationNumber="2020123456",
            inventionTitle="Test Invention",
            filingDate="20200115",
        )
        assert data.application_number == "2020123456"
        assert data.invention_title == "Test Invention"

    def test_nested_lists_default_empty(self) -> None:
        data = PatentProgressData(applicationNumber="2020123456")
        assert data.applicant_attorney == []
        assert data.priority_right_information == []
        assert data.divisional_application_information == []
        assert data.bibliography_information == []
        assert data.parent_application_information is None

    def test_with_real_priority_payload(self) -> None:
        data = PatentProgressData.model_validate(
            {
                "applicationNumber": "2020123456",
                "inventionTitle": "立体配線構造体の製造方法",
                "applicantAttorney": [
                    {
                        "applicantAttorneyCd": "000114400",
                        "name": "メイショウ株式会社",
                        "applicantAttorneyClass": "1",
                    }
                ],
                "priorityRightInformation": [
                    {
                        "nationalPriorityLawCd": "1",
                        "nationalPriorityApplicationNumber": "2019210418",
                        "nationalPriorityDate": "20191121",
                    }
                ],
                "bibliographyInformation": [
                    {
                        "numberType": "01",
                        "number": "2020123456",
                        "documentList": [],
                    }
                ],
                "parentApplicationInformation": {},
                "divisionalApplicationInformation": [],
            }
        )
        assert len(data.applicant_attorney) == 1
        assert data.applicant_attorney[0].name == "メイショウ株式会社"
        assert len(data.priority_right_information) == 1
        assert (
            data.priority_right_information[0].national_priority_application_number == "2019210418"
        )
        assert len(data.bibliography_information) == 1
        # Empty parentApplicationInformation object materialises to a stub
        # ParentApplicationInfo (not None) — that's acceptable.
        assert data.parent_application_information is not None
        assert data.parent_application_information.parent_application_number == ""


class TestSimplifiedPatentProgressData:
    """SimplifiedPatentProgressData inherits from PatentProgressData."""

    def test_creates_model(self) -> None:
        data = SimplifiedPatentProgressData(
            applicationNumber="2020123456",
            inventionTitle="Test",
        )
        assert data.application_number == "2020123456"
        assert isinstance(data, PatentProgressData)

    def test_no_priority_field_in_simple(self) -> None:
        data = SimplifiedPatentProgressData.model_validate(
            {
                "applicationNumber": "2020123456",
                "inventionTitle": "Test",
                "bibliographyInformation": [],
            }
        )
        # priority field present but empty by default
        assert data.priority_right_information == []


# =============================================================================
# Divisional info (top-level wrapper)
# =============================================================================


class TestDivisionalAppInfoData:
    def test_empty(self) -> None:
        data = DivisionalAppInfoData.model_validate(
            {
                "applicationNumber": "2020123456",
                "parentApplicationInformation": {},
                "divisionalApplicationInformation": [],
            }
        )
        assert data.application_number == "2020123456"
        assert data.divisional_application_information == []
        assert data.parent_application_information is not None

    def test_with_descendants(self) -> None:
        data = DivisionalAppInfoData.model_validate(
            {
                "applicationNumber": "2020123456",
                "divisionalApplicationInformation": [
                    {"applicationNumber": "2021100000", "divisionalGeneration": "1"},
                    {"applicationNumber": "2022200000", "divisionalGeneration": "2"},
                ],
            }
        )
        assert len(data.divisional_application_information) == 2


# =============================================================================
# Number reference
# =============================================================================


class TestNumberReference:
    """NumberReference is now a single object, not wrapped in caseNumberReference."""

    def test_creates_from_alias(self) -> None:
        ref = NumberReference(
            applicationNumber="2020123456",
            publicationNumber="2021090037",
            registrationNumber="7533889",
        )
        assert ref.application_number == "2020123456"
        assert ref.publication_number == "2021090037"
        assert ref.registration_number == "7533889"

    def test_design_fields(self) -> None:
        # Design endpoint has internationalRegistrationNumber + designNumber
        ref = NumberReference(
            applicationNumber="2020012345",
            internationalRegistrationNumber="DM/123",
            designNumber="D1",
        )
        assert ref.international_registration_number == "DM/123"
        assert ref.design_number == "D1"


# =============================================================================
# Citations
# =============================================================================


class TestPatentCitedDocument:
    def test_basic(self) -> None:
        cite = PatentCitedDocument(
            draftDate="20240220",
            citationType="19",
            citationOrder="1",
            documentNumber="JPA 414233033",
        )
        assert cite.citation_type == "19"
        assert cite.document_number == "JPA 414233033"


class TestNonPatentCitedDocument:
    def test_basic(self) -> None:
        cite = NonPatentCitedDocument(
            draftDate="20240220",
            citationType="35",
            citationOrder="1",
            authorName="John Doe",
            paperTitle="Title",
            publicationName="Pub",
        )
        assert cite.author_name == "John Doe"
        assert cite.paper_title == "Title"


class TestCitedDocumentsData:
    def test_with_arrays(self) -> None:
        # Real API returns arrays under patentDoc / nonPatentDoc.
        data = CitedDocumentsData.model_validate(
            {
                "applicationNumber": "2020123456",
                "patentDoc": [
                    {"draftDate": "20240220", "citationType": "19", "documentNumber": "JPA 1"}
                ],
                "nonPatentDoc": [],
            }
        )
        assert len(data.patent_doc) == 1
        assert data.patent_doc[0].document_number == "JPA 1"
        assert data.non_patent_doc == []


# =============================================================================
# Registration
# =============================================================================


class TestRegistrationInfo:
    def test_patent_shape(self) -> None:
        reg = RegistrationInfo.model_validate(
            {
                "applicationNumber": "2020123456",
                "filingDate": "20200720",
                "registrationNumber": "7533889",
                "registrationDate": "20240805",
                "decisionDate": "20240704",
                "rightPersonInformation": [
                    {"rightPersonCd": "000114400", "rightPersonName": "メイショウ株式会社"}
                ],
                "inventionTitle": "立体配線構造体の製造方法",
                "numberOfClaims": "005",
                "expireDate": "20400720",
                "nextPensionPaymentDate": "20270805",
                "lastPaymentYearly": "03",
                "erasureIdentifier": "00",
                "updateDate": "20240821",
            }
        )
        assert reg.registration_number == "7533889"
        assert reg.number_of_claims == "005"
        assert len(reg.right_person_information) == 1
        assert reg.right_person_information[0].right_person_name == "メイショウ株式会社"

    def test_design_shape(self) -> None:
        reg = RegistrationInfo.model_validate(
            {
                "applicationNumber": "2020012345",
                "registrationNumber": "1680736",
                "designArticle": "球体転がし用積み木",
            }
        )
        assert reg.design_article == "球体転がし用積み木"


# =============================================================================
# PCT national phase
# =============================================================================


class TestPctNationalPhaseData:
    def test_minimal(self) -> None:
        data = PctNationalPhaseData(applicationNumber="2021550001")
        assert data.application_number == "2021550001"
        # Backwards-compat alias.
        assert data.national_application_number == "2021550001"


# =============================================================================
# Document bundle
# =============================================================================


class TestDocumentBundleResult:
    def test_inline_zip(self) -> None:
        bundle = DocumentBundleResult(
            application_number="2020123456",
            zip_bytes=b"PK\x03\x04...",
            content_type="application/zip",
        )
        assert bundle.zip_bytes is not None
        assert bundle.is_empty is False

    def test_oversize_redirect(self) -> None:
        bundle = DocumentBundleResult(
            application_number="2020123456",
            download_url="https://example.com/big.zip",
            content_type="application/json",
        )
        assert bundle.zip_bytes is None
        assert bundle.download_url == "https://example.com/big.zip"
        assert bundle.is_empty is False

    def test_empty(self) -> None:
        bundle = DocumentBundleResult(application_number="2020123456")
        assert bundle.is_empty is True


# =============================================================================
# Design / trademark
# =============================================================================


class TestDesignProgressData:
    def test_real_payload(self) -> None:
        data = DesignProgressData.model_validate(
            {
                "applicationNumber": "2020015234",
                "designArticle": "球体転がし用積み木",
                "designClass": "E2112",
                "filingDate": "20200624",
                "registrationNumber": "1680736",
                "registrationDate": "20210219",
                "principalDesignApplicationNumber": "",
            }
        )
        assert data.application_number == "2020015234"
        assert data.design_article == "球体転がし用積み木"
        assert data.design_class == "E2112"
        # Backwards-compat alias.
        assert data.design_title == "球体転がし用積み木"


class TestTrademarkProgressData:
    def test_real_payload(self) -> None:
        data = TrademarkProgressData.model_validate(
            {
                "applicationNumber": "2024123456",
                "trademarkForDisplay": "メタンレス和牛",
                "transliteration": {"0": "メタンレス", "1": "メタンレスワギュー"},
                "viennaClass": {},
                "goodsServiceInformation": [
                    {
                        "goodsServiceClass": "29",
                        "goodsServiceName": "牛肉",
                        "similarCode": "32A01",
                    }
                ],
                "filingDate": "20241118",
            }
        )
        assert data.trademark_for_display == "メタンレス和牛"
        # Backwards-compat alias.
        assert data.trademark_name == "メタンレス和牛"
        assert data.transliteration == {"0": "メタンレス", "1": "メタンレスワギュー"}
        assert len(data.goods_service_information) == 1
        # Flat backwards-compat list.
        assert data.goods_services == ["牛肉"]
