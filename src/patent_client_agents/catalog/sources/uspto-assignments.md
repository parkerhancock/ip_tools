# USPTO Patent Assignments

Patent ownership transfer records from the USPTO Assignment Center. Covers assignments, security interests, licenses, and other recorded conveyances.

## Source

| | |
|---|---|
| Module | `patent_client_agents.uspto_assignments` |
| Client | `AssignmentCenterClient` |
| Base URL | `https://assignmentcenter.uspto.gov` |
| Auth | None |
| Rate limits | Not published |
| Status | Active |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ipas/search/api/v2/public/patent/exportPublicPatentData` | Search patent assignment records |

## Library API

```python
from patent_client_agents.uspto_assignments import AssignmentCenterClient

async with AssignmentCenterClient() as client:
    records = await client.search_by_assignee("Apple Inc")
    records = await client.search_by_patent("10000000")
```

| Method | Returns | Description |
|--------|---------|-------------|
| `search_by_assignee(assignee_name, start_row=1, limit=100)` | `list[AssignmentRecord]` | Search by assignee (receiving party) |
| `search_by_assignor(assignor_name, start_row=1, limit=100)` | `list[AssignmentRecord]` | Search by assignor (transferring party) |
| `search_by_patent(patent_number, limit=100)` | `list[AssignmentRecord]` | Search by patent number |
| `search_by_application(application_number, limit=100)` | `list[AssignmentRecord]` | Search by application number |
| `search_by_reel_frame(reel_frame)` | `list[AssignmentRecord]` | Search by reel/frame (e.g. "52614/446") |
| `search(assignee_name=, assignor_name=, patent_number=, ...)` | `list[AssignmentRecord]` | Multi-criteria search |
| `search_all(assignee_name=, assignor_name=, batch_size=1000, max_results=)` | `list[AssignmentRecord]` | Auto-paginated search |

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_patent_assignments(assignee?, assignor?, patent_number?, application_number?, reel_frame?, paginate_all?)` | Unified patent-assignment search. Set exactly one filter. `paginate_all=True` auto-paginates for assignee/assignor searches. |
