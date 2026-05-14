"""Federal Circuit (CAFC) opinion client with patent case classification.

Scrapes opinions from the CAFC website via its WordPress DataTables API,
classifies them as patent-related using keyword confidence scoring, and
provides PDF download.
"""

from patent_client_agents.cafc.classifier import PatentClassifier
from patent_client_agents.cafc.client import CAFCClient, CAFCError
from patent_client_agents.cafc.models import CAFCOpinion

__all__ = [
    "CAFCClient",
    "CAFCError",
    "CAFCOpinion",
    "PatentClassifier",
]
