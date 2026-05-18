"""Async INPI France national TM + Design connector (BYOK).

Wraps ``api-gateway.inpi.fr`` for French national trademarks (WIPO ST.66
v1.0) and designs (WIPO ST.86 v1.0). Authentication is a session-bearer
+ XSRF flow bound to a personal ``data.inpi.fr`` account (NOT PISTE);
the XSRF + bearer + refresh lifecycle is implemented in chunk 3.

**TM + design only — patents covered via EPO OPS.** For FR patent
coverage, use ``patent_client_agents.epo_ops`` (country code ``FR``);
INPADOC covers EP-routed FR designations and FR national-route filings
with adequate fidelity.

Environment Variables:
    INPI_USERNAME: personal data.inpi.fr account username
    INPI_PASSWORD: personal data.inpi.fr account password
"""

from .models import InpiDesignRow, InpiTrademarkRow

# NOTE: ``InpiPiClient`` is intentionally not re-exported here yet —
# chunk 3 rewrites ``client.py`` (and ``api.py``) and will add the
# client + module-level helper re-exports at that point. Importing the
# JPO-template client.py / api.py mid-build would surface unrelated
# JPO-shaped APIs and confuse downstream consumers.

__all__ = [
    "InpiTrademarkRow",
    "InpiDesignRow",
]
