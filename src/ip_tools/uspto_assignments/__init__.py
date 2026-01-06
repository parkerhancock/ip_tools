"""USPTO Patent Assignment Search API client.

This module provides access to patent assignment records via the USPTO
Assignment Search API. Data is available from August 1980 to present.

Two approaches for accessing assignment data:

1. **USPTO ODP** (via `ip_tools.uspto_odp`):
   - Endpoint: `/api/v1/patent/applications/{appNum}/assignment`
   - Lookup by application number only
   - Part of the unified ODP client

2. **Assignment Search API** (this module):
   - Endpoint: `assignment-api.uspto.gov/patent/lookup`
   - Search by patent number, application number, or assignee name
   - Broader search capabilities

Example:
    # Using the Assignment Search API
    from ip_tools.uspto_assignments import UsptoAssignmentsClient

    async with UsptoAssignmentsClient() as client:
        # By patent number
        records = await client.assignments_for_patent("US8830957")

        # By application number
        records = await client.assignments_for_application("16123456")

        # By assignee name
        records = await client.assignments_for_assignee("Apple Inc")

    # Using USPTO ODP (alternative)
    from ip_tools.uspto_odp import UsptoOdpClient

    async with UsptoOdpClient() as client:
        response = await client.get_assignment("16123456")
"""

from .client import UsptoAssignmentsClient
from .models import AssignmentParty, AssignmentRecord

__all__ = [
    "UsptoAssignmentsClient",
    "AssignmentParty",
    "AssignmentRecord",
]
