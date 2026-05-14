"""UPC statutes corpus connector (MCP-free public surface)."""

from .api import (
    USAGE_RESOURCE_URI,
    InstrumentInput,
    StatuteSearchInput,
    UpcCorpusMeta,
    UpcInstrument,
    UpcInstrumentText,
    UpcStatutesClient,
    UpcStatuteSearchHit,
    UpcStatuteSearchResponse,
    get_client,
    get_instrument,
    get_usage_resource,
    list_instruments,
    search,
)
from .corpus import CorpusUnavailable

__all__ = [
    "UpcStatutesClient",
    "CorpusUnavailable",
    "UpcInstrument",
    "UpcInstrumentText",
    "UpcCorpusMeta",
    "UpcStatuteSearchHit",
    "UpcStatuteSearchResponse",
    "StatuteSearchInput",
    "InstrumentInput",
    "get_client",
    "search",
    "get_instrument",
    "list_instruments",
    "USAGE_RESOURCE_URI",
    "get_usage_resource",
]
