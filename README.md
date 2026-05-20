<p align="center">
  <img src="https://raw.githubusercontent.com/ANML-Foundation/.github/main/images/anml-foundation-logo.png" alt="ANML Foundation" width="300">
</p>

<h1 align="center">anml-client</h1>

<p align="center">
  <strong>ANML 1.0 client library for Python</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/anml-client/"><img src="https://img.shields.io/pypi/v/anml-client" alt="PyPI"></a>
  <a href="https://pypi.org/project/anml-client/"><img src="https://img.shields.io/pypi/pyversions/anml-client" alt="Python"></a>
  <a href="https://github.com/ANML-Foundation/anml-client-python/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ANML-Foundation/anml-client-python" alt="License"></a>
</p>

---

A modern, async-first Python client for the [ANML (Agent Negotiation Markup Language)](https://anmlfoundation.org) 1.0 specification. Built for AI agents that need to discover, negotiate, and interact with machine-first web services.

## Features

- **Async-first** — Built on httpx for modern async HTTP
- **Type-safe** — Full Pydantic v2 models for all ANML types
- **Secure** — defusedxml for safe XML parsing, HTTPS enforcement, SRI verification
- **Discovery** — Well-known, Link header, and HTML link discovery
- **Disclosure** — Consent management and disclosure evaluation
- **Flow navigation** — Step-by-step flow traversal utilities
- **Pagination** — Async iteration over nav links
- **Builder pattern** — Fluent client configuration

## Installation

```bash
pip install anml-client
```

## Quick Start

```python
import asyncio
from anml_client import AnmlClient, AllowListTrustPolicy

async def main():
    # Build a client with trust policy
    client = (
        AnmlClient.builder()
        .base_url("https://api.example.com")
        .trust_policy(AllowListTrustPolicy(["example.com"]))
        .build()
    )

    async with client:
        # Discover ANML endpoint
        anml_url = await client.discover("https://example.com")
        if anml_url:
            # Fetch and parse the ANML document
            doc = await client.fetch_url(anml_url)

            # Navigate flows
            from anml_client import FlowNavigator
            nav = FlowNavigator(doc)
            print(f"Current step: {nav.current_step}")
            print(f"Flow complete: {nav.is_complete}")

            # Execute actions
            response = await client.execute_action(
                doc, "get-profile", params={"user_id": "123"}
            )
            print(f"Response: {response.status_code}")

            # Paginate through results
            async for page in client.paginate(doc):
                print(f"Next page: {page.head.title}")

asyncio.run(main())
```

## Parsing ANML Documents

```python
from anml_client import parse_anml_xml, parse_anml_json

# Parse XML
doc = parse_anml_xml(xml_string)

# Parse JSON
doc = parse_anml_json(json_string)

# Auto-detect from content type
from anml_client import parse_anml
doc = parse_anml(content, "application/anml+xml")
```

## Disclosure & Consent

```python
from anml_client import ConsentStore, evaluate_disclosure, AllowAllTrustPolicy

store = ConsentStore()
store.grant("email", purpose="communication")

# Evaluate disclosures in a document
from anml_client import evaluate_all_disclosures
results = evaluate_all_disclosures(doc, store, AllowAllTrustPolicy())
```

## SRI Verification

```python
from anml_client import compute_sri, verify_sri

# Compute integrity hash
sri = compute_sri(data, "sha256")

# Verify data integrity
is_valid = verify_sri(data, "sha256-...")
```

## API Overview

| Module | Description |
|--------|-------------|
| `anml_client.client` | Main `AnmlClient` with builder pattern |
| `anml_client.types` | Pydantic models for all ANML 1.0 types |
| `anml_client.parser` | XML and JSON parsing |
| `anml_client.config` | Client configuration and trust policies |
| `anml_client.discovery` | ANML endpoint discovery |
| `anml_client.disclosure` | Consent management and disclosure evaluation |
| `anml_client.action` | Action execution with parameter binding |
| `anml_client.flow` | Flow navigation utilities |
| `anml_client.knowledge` | Knowledge exchange helpers |
| `anml_client.integrity` | SRI verification (SHA-256/384/512) |
| `anml_client.pagination` | Async pagination over nav links |
| `anml_client.middleware` | HTTP middleware chain |
| `anml_client.errors` | Exception hierarchy |

## Links

- [ANML Foundation](https://anmlfoundation.org)
- [ANML Specification](https://anmlfoundation.org/docs)
- [GitHub Repository](https://github.com/ANML-Foundation/anml-client-python)

## License

ISC
