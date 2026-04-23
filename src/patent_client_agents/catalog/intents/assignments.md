# Patent Assignments

Single unified search over the USPTO Assignment Center, replacing what used
to be six different `search_by_*` tools.

## Why fused

All six previous tools (`search_patent_assignments_by_assignee`, `…_assignor`,
`…_patent`, `…_application`, `…_reel_frame`, plus `search_all_*`) hit the
same `AssignmentCenterClient` with different filter arguments. The shape of
the returned records is identical across filters. This is **parameter fusion
within a single source**, not cross-source fusion — pure win, no
information loss.

## MCP tool

```
search_patent_assignments(
    assignee?, assignor?, patent_number?, application_number?, reel_frame?,
    paginate_all=False,
) -> dict
```

**Exactly one** filter must be set; validation raises otherwise. Records
include reel/frame, recording date, conveyance type, assignor/assignee
identities, and affected properties (applications and patents).

`paginate_all=True` auto-paginates assignee/assignor searches through all
matching results; ignored for patent/application/reel_frame lookups which
are already single-record-bounded.

## Python API (raw)

No fused wrapper in the library — if you're a Python consumer, call the
underlying client directly:

```python
from patent_client_agents.uspto_assignments import AssignmentCenterClient

async with AssignmentCenterClient() as client:
    records = await client.search_by_assignee("Anthropic PBC")
```

The MCP wrapper exists only to collapse five decorated tools into one; the
library doesn't benefit from that re-wrapping.

## Related

- `get_patent_assignment(application_number)` — **different source**. Uses
  USPTO ODP (embedded assignment data on the application record), not
  Assignment Center (raw recordation records). Both answer "who owns this
  patent?" but return different shapes; they are deliberately kept
  separate.
