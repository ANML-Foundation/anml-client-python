"""ANML discovery via well-known, Link headers, and HTML link elements."""

from __future__ import annotations

import re
from urllib.parse import urljoin

import httpx

from anml_client.errors import DiscoveryError

# Link header pattern: <url>; rel="anml"
_LINK_HEADER_PATTERN = re.compile(
    r'<([^>]+)>\s*;\s*rel\s*=\s*"?anml"?', re.IGNORECASE
)

# HTML link pattern: <link rel="anml" href="...">
_HTML_LINK_PATTERN = re.compile(
    r'<link[^>]+rel\s*=\s*["\']anml["\'][^>]+href\s*=\s*["\']([^"\']+)["\']',
    re.IGNORECASE,
)

# Also match href before rel
_HTML_LINK_PATTERN_ALT = re.compile(
    r'<link[^>]+href\s*=\s*["\']([^"\']+)["\'][^>]+rel\s*=\s*["\']anml["\']',
    re.IGNORECASE,
)


async def discover_well_known(client: httpx.AsyncClient, base_url: str) -> str | None:
    """Attempt ANML discovery via /.well-known/anml.

    Args:
        client: The HTTP client to use.
        base_url: The base URL to discover from.

    Returns:
        The ANML document URL if found, None otherwise.
    """
    url = urljoin(base_url.rstrip("/") + "/", ".well-known/anml")
    try:
        response = await client.get(url, follow_redirects=True)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "anml" in content_type or "xml" in content_type or "json" in content_type:
                return str(response.url)
            # If it's a redirect target or has content, return the URL
            return str(response.url)
    except httpx.HTTPError:
        pass
    return None


async def discover_link_header(response: httpx.Response) -> str | None:
    """Extract ANML URL from Link response headers.

    Args:
        response: An HTTP response to check for Link headers.

    Returns:
        The ANML document URL if found, None otherwise.
    """
    link_header = response.headers.get("link", "")
    if not link_header:
        return None

    match = _LINK_HEADER_PATTERN.search(link_header)
    if match:
        return match.group(1)
    return None


def discover_html_link(html: str) -> str | None:
    """Extract ANML URL from HTML link elements.

    Args:
        html: HTML content to search for ANML link elements.

    Returns:
        The ANML document URL if found, None otherwise.
    """
    match = _HTML_LINK_PATTERN.search(html)
    if match:
        return match.group(1)

    match = _HTML_LINK_PATTERN_ALT.search(html)
    if match:
        return match.group(1)

    return None


async def discover(client: httpx.AsyncClient, base_url: str) -> str | None:
    """Attempt full ANML discovery using all methods.

    Tries in order:
    1. Well-known endpoint
    2. Link header on base URL
    3. HTML link element on base URL

    Args:
        client: The HTTP client to use.
        base_url: The base URL to discover from.

    Returns:
        The ANML document URL if found, None otherwise.

    Raises:
        DiscoveryError: If discovery encounters an unrecoverable error.
    """
    # Try well-known first
    result = await discover_well_known(client, base_url)
    if result:
        return result

    # Try fetching the base URL and checking headers/content
    try:
        response = await client.get(base_url, follow_redirects=True)
    except httpx.HTTPError as e:
        raise DiscoveryError(f"Failed to fetch base URL for discovery: {e}") from e

    # Check Link header
    link_url = await discover_link_header(response)
    if link_url:
        return urljoin(base_url, link_url)

    # Check HTML content for link element
    content_type = response.headers.get("content-type", "")
    if "html" in content_type:
        html_url = discover_html_link(response.text)
        if html_url:
            return urljoin(base_url, html_url)

    return None
