"""Async KIPO KIPRIS Plus connector (Korean Intellectual Property Office).

Scaffold copied from the JPO package; XML response models, the
``KiprisClient`` rewrite, MCP tool surface, and tests land in chunks
2-4. See ``research/specs/kr-kipo-connector-spec.md`` for the full
contract. Auth is BYOK per ToS §11: a single per-user ``serviceKey``
exposed via the ``KIPO_KIPRIS_API_KEY`` environment variable.
"""

from .api import (  # noqa: F401
    # Models
    ApplicantAttorney,
    CaseNumberKind,
    CitedDocumentsData,
    DesignProgressData,
    DivisionalAppInfoData,
    DocumentBundleResult,
    # Client
    KiprisClient,
    NumberReference,
    # Enums
    NumberType,
    ParentApplicationInfo,
    PatentProgressData,
    PctKind,
    PctNationalPhaseData,
    PriorityInfo,
    RegistrationInfo,
    SimplifiedPatentProgressData,
    StatusCode,
    TrademarkProgressData,
    get_design_applicant_by_code,
    get_design_applicant_by_name,
    # Design functions
    get_design_application_documents,
    get_design_jplatpat_url,
    get_design_mailed_documents,
    get_design_number_reference,
    get_design_priority_info,
    get_design_progress,
    get_design_progress_simple,
    get_design_refusal_notices,
    get_design_registration_info,
    get_patent_applicant_by_code,
    get_patent_applicant_by_name,
    # Patent functions
    get_patent_application_documents,
    get_patent_cited_documents,
    get_patent_divisional_info,
    get_patent_jplatpat_url,
    get_patent_mailed_documents,
    get_patent_number_reference,
    get_patent_pct_national_number,
    get_patent_priority_info,
    get_patent_progress,
    get_patent_progress_simple,
    get_patent_refusal_notices,
    get_patent_registration_info,
    get_trademark_applicant_by_code,
    get_trademark_applicant_by_name,
    # Trademark functions
    get_trademark_application_documents,
    get_trademark_jplatpat_url,
    get_trademark_mailed_documents,
    get_trademark_number_reference,
    get_trademark_priority_info,
    get_trademark_progress,
    get_trademark_progress_simple,
    get_trademark_refusal_notices,
    get_trademark_registration_info,
)
from .documents import parse_document_bundle  # noqa: F401
from .models_documents import (  # noqa: F401
    DocumentBundle,
    DocumentEntry,
    DocumentKind,
    IpType,
)

__all__ = [
    # Client
    "KiprisClient",
    # Enums
    "StatusCode",
    "NumberType",
    "CaseNumberKind",
    "PctKind",
    # Models
    "PatentProgressData",
    "SimplifiedPatentProgressData",
    "DesignProgressData",
    "TrademarkProgressData",
    "ApplicantAttorney",
    "PriorityInfo",
    "ParentApplicationInfo",
    "DivisionalAppInfoData",
    "NumberReference",
    "DocumentBundleResult",
    "CitedDocumentsData",
    "RegistrationInfo",
    "PctNationalPhaseData",
    # Document parsing
    "DocumentBundle",
    "DocumentEntry",
    "DocumentKind",
    "IpType",
    "parse_document_bundle",
    # Patent functions
    "get_patent_progress",
    "get_patent_progress_simple",
    "get_patent_divisional_info",
    "get_patent_priority_info",
    "get_patent_applicant_by_code",
    "get_patent_applicant_by_name",
    "get_patent_number_reference",
    "get_patent_application_documents",
    "get_patent_mailed_documents",
    "get_patent_refusal_notices",
    "get_patent_cited_documents",
    "get_patent_registration_info",
    "get_patent_jplatpat_url",
    "get_patent_pct_national_number",
    # Design functions
    "get_design_progress",
    "get_design_progress_simple",
    "get_design_priority_info",
    "get_design_applicant_by_code",
    "get_design_applicant_by_name",
    "get_design_number_reference",
    "get_design_application_documents",
    "get_design_mailed_documents",
    "get_design_refusal_notices",
    "get_design_registration_info",
    "get_design_jplatpat_url",
    # Trademark functions
    "get_trademark_progress",
    "get_trademark_progress_simple",
    "get_trademark_priority_info",
    "get_trademark_applicant_by_code",
    "get_trademark_applicant_by_name",
    "get_trademark_number_reference",
    "get_trademark_application_documents",
    "get_trademark_mailed_documents",
    "get_trademark_refusal_notices",
    "get_trademark_registration_info",
    "get_trademark_jplatpat_url",
]
