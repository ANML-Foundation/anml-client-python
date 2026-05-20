"""Async iteration over ANML navigation links."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from anml_client.types import AnmlDocument

if TYPE_CHECKING:
    import httpx

    from anml_client.parser import parse_anml


async def paginate(
    http_client: "httpx.AsyncClient",
    doc: AnmlDocument,
    parse_fn: "type[None] | None" = None,
) -> AsyncGenerator[AnmlDocument, None]:
    """Async generator that follows nav.next links to paginate through documents.

    Args:
        http_client: The HTTP client to use for fetching.
        doc: The initial ANML document.
        parse_fn: Not used, kept for API compatibility.

    Yields:
        Each subsequent ANML document in the pagination chain.
    """
    from anml_client.parser import parse_anml as _parse_anml

    current = doc
    visited: set[str] = set()

    while current.nav and current.nav.next:
        next_url = current.nav.next
        if next_url in visited:
            break
        visited.add(next_url)

        response = await http_client.get(next_url, follow_redirects=True)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "application/anml+xml")
        current = _parse_anml(response.text, content_type)
        yield current
