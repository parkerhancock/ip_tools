# IP Tools

**Intellectual property data tools built for AI agents.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-ty-blue.svg)](https://github.com/astral-sh/ty)

## Overview

IP Tools provides async Python APIs for accessing intellectual property data sources. Unlike traditional libraries designed for human developers, IP Tools is built with **AI agents as the primary consumer**.

### Inspiration

This project draws from [patent_client](https://github.com/parkerhancock/patent_client), a comprehensive Python library for patent data. IP Tools reimagines that functionality through an agent-first lens:

- **Simplified APIs** - Clean async interfaces that agents can easily invoke
- **Structured output** - Pydantic models optimized for LLM consumption
- **Skill integration** - Built-in Claude Code skill for natural language access
- **No CLI** - Pure library APIs; agents don't need command-line interfaces

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code Agent                        │
├─────────────────────────────────────────────────────────────┤
│                    IP Tools Skill                            │
│         (Natural language → Python scriptlets)               │
├─────────────────────────────────────────────────────────────┤
│                   ip_tools Library                           │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│    │  USPTO   │  │   EPO    │  │  Google  │  │   JPO    │   │
│    │   ODP    │  │   OPS    │  │ Patents  │  │          │   │
│    └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Source Coverage

### Google Patents
| Feature | Status | Description |
|---------|--------|-------------|
| Patent lookup | ✅ | Fetch by publication number |
| Full-text search | ✅ | Keyword, assignee, inventor search |
| Claims & description | ✅ | Full-text content |
| Citations | ✅ | Forward and backward citations |
| Patent families | ✅ | Related applications |
| PDF download | ✅ | Full document PDFs |

### USPTO Open Data Portal (ODP)
| Feature | Status | Description |
|---------|--------|-------------|
| **Applications** | | |
| Application search | ✅ | Search by number, date, status |
| Application details | ✅ | Bibliographic data, status |
| Continuity data | ✅ | Parent/child relationships |
| Foreign priority | ✅ | Priority claims |
| Assignments | ✅ | Ownership records |
| Attorneys | ✅ | Attorney/agent of record |
| Transactions | ✅ | Office action history |
| Adjustments | ✅ | PTA/PTE data |
| **PTAB Trials** | | |
| IPR/PGR/CBM search | ✅ | Search inter partes reviews |
| Trial details | ✅ | Party info, status, decisions |
| Trial documents | ✅ | Petitions, responses, decisions |
| **PTAB Appeals** | | |
| Appeal search | ✅ | Ex parte appeals |
| Appeal details | ✅ | Status, decisions |
| **Bulk Data** | | |
| Bulk downloads | ✅ | XML/JSON data packages |
| Full-text grants | ✅ | Weekly patent grants |
| Full-text applications | ✅ | Weekly applications |

### USPTO Assignments
| Feature | Status | Description |
|---------|--------|-------------|
| Assignment search | ✅ | Search by reel/frame, patent |
| Assignment details | ✅ | Parties, conveyance type |
| Property lookup | ✅ | Patents in assignment |

### EPO OPS (Open Patent Services)
| Feature | Status | Description |
|---------|--------|-------------|
| **Published Data (Inpadoc)** | | |
| Patent search | ✅ | CQL query search |
| Family search | ✅ | Search grouped by family |
| Bibliographic data | ✅ | Titles, abstracts, parties |
| Claims | ✅ | Full claim text |
| Description | ✅ | Full description text |
| Legal events | ✅ | Status changes, fees |
| Patent families | ✅ | INPADOC family members |
| PDF download | ✅ | Full document PDFs |
| Number conversion | ✅ | Format conversion |
| **EP Register** | | |
| Register search | ✅ | Search EP applications |
| Register biblio | ✅ | Detailed EP data |
| Procedural steps | ✅ | Prosecution history |
| Register events | ✅ | EPO Bulletin events |
| Designated states | ✅ | Validation countries |
| Opposition data | ✅ | Opposition proceedings |
| Unitary Patent | ✅ | UPP status and states |
| **Classification** | | |
| CPC lookup | ✅ | Classification hierarchy |
| CPC search | ✅ | Keyword search |
| CPC mapping | ✅ | CPC/IPC/ECLA conversion |

### JPO (Japan Patent Office)
| Feature | Status | Description |
|---------|--------|-------------|
| Patent progress | ✅ | Application status |
| Examination history | ✅ | Office actions |
| Documents | ✅ | Filed documents |
| Citations | ✅ | Cited prior art |
| Family info | ✅ | Divisionals, priorities |
| Registration | ✅ | Grant details |
| PCT national phase | ✅ | JP national entry lookup |
| Design/trademark | ✅ | Similar methods available |

### Cross-Source Features
| Feature | Status | Description |
|---------|--------|-------------|
| HTTP caching | ✅ | SQLite-backed with TTL |
| Cache statistics | ✅ | Hit rate, size monitoring |
| Cache invalidation | ✅ | Pattern-based clearing |
| Rate limiting | ✅ | Built-in throttling |
| Retry logic | ✅ | Automatic retries |

## Quick Start

```python
from ip_tools.google_patents import GooglePatentsClient

async with GooglePatentsClient() as client:
    # Fetch a specific patent
    patent = await client.fetch("US10123456B2")
    print(patent.title)
    print(patent.abstract)

    # Search patents
    results = await client.search("machine learning neural network")
    async for patent in results:
        print(f"{patent.publication_number}: {patent.title}")
```

## Installation

```bash
pip install ip-tools
```

### As a Claude Code Plugin

```bash
claude plugins add ip-tools
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `EPO_OPS_API_KEY` | For EPO | EPO OPS consumer key |
| `EPO_OPS_API_SECRET` | For EPO | EPO OPS consumer secret |
| `JPO_API_USERNAME` | For JPO | JPO API username |
| `JPO_API_PASSWORD` | For JPO | JPO API password |

## For Agents

When installed as a Claude Code plugin, agents can access IP data through natural language:

```
User: Find patents related to transformer neural networks from 2023

Agent: [Uses ip_tools skill to search Google Patents and return structured results]
```

The skill handles:
- Query construction
- API selection
- Result formatting
- Error handling

## Design Principles

- **100% Async** - All APIs are async-first with no sync wrappers
- **Fully Typed** - Complete type annotations checked with `ty`
- **Fully Tested** - Comprehensive test coverage with `pytest-asyncio`
- **Agent-Optimized** - Output formats designed for LLM parsing
- **Cacheable** - Built-in HTTP caching for efficient repeated queries

## Development

```bash
# Clone the repository
git clone https://github.com/parkerhancock/ip_tools.git
cd ip_tools

# Install dependencies with uv
uv sync --group dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format .

# Run type checking
uv run ty check
```

## Related Projects

- [patent_client](https://github.com/parkerhancock/patent_client) - The original patent data library

## License

Apache-2.0
