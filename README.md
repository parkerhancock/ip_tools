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
│    │ Patents  │  │   OPS    │  │ Patents  │  │          │   │
│    └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Features

### Data Sources

| Source | Coverage | Status |
|--------|----------|--------|
| **USPTO** | Patents, applications, assignments, prosecution history | Planned |
| **EPO OPS** | European patents, patent families, legal status | Planned |
| **Google Patents** | Global patent search, full-text, citations | Planned |
| **JPO** | Japanese patents and applications | Planned |

### Design Principles

- **100% Async** - All APIs are async-first with no sync wrappers
- **Fully Typed** - Complete type annotations checked with `ty`
- **Fully Tested** - Comprehensive test coverage with `pytest-asyncio`
- **Agent-Optimized** - Output formats designed for LLM parsing
- **Cacheable** - Built-in HTTP caching for efficient repeated queries

## Installation

```bash
pip install ip-tools
```

### As a Claude Code Plugin

```bash
claude plugins add ip-tools
```

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

## Project Status

IP Tools is under active development. See [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md) for the roadmap.

## Related Projects

- [patent_client](https://github.com/parkerhancock/patent_client) - The original patent data library

## License

Apache-2.0
