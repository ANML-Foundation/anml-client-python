"""Tests for ANML discovery."""

import httpx
import pytest

from anml_client.discovery import discover_html_link, discover_link_header


class TestDiscoverLinkHeader:
    """Tests for Link header discovery."""

    @pytest.mark.asyncio
    async def test_discover_link_header_found(self) -> None:
        """Find ANML URL in Link header."""
        response = httpx.Response(
            200,
            headers={"link": '<https://example.com/api.anml>; rel="anml"'},
        )
        result = await discover_link_header(response)
        assert result == "https://example.com/api.anml"

    @pytest.mark.asyncio
    async def test_discover_link_header_no_anml(self) -> None:
        """Return None when no ANML link in header."""
        response = httpx.Response(
            200,
            headers={"link": '<https://example.com/style.css>; rel="stylesheet"'},
        )
        result = await discover_link_header(response)
        assert result is None

    @pytest.mark.asyncio
    async def test_discover_link_header_missing(self) -> None:
        """Return None when no Link header present."""
        response = httpx.Response(200, headers={})
        result = await discover_link_header(response)
        assert result is None

    @pytest.mark.asyncio
    async def test_discover_link_header_multiple_links(self) -> None:
        """Find ANML URL among multiple Link headers."""
        response = httpx.Response(
            200,
            headers={
                "link": '<https://example.com/style.css>; rel="stylesheet", <https://example.com/api.anml>; rel="anml"'
            },
        )
        result = await discover_link_header(response)
        assert result == "https://example.com/api.anml"


class TestDiscoverHtmlLink:
    """Tests for HTML link element discovery."""

    def test_discover_html_link_found(self) -> None:
        """Find ANML URL in HTML link element."""
        html = '<html><head><link rel="anml" href="/api/document.anml"></head></html>'
        result = discover_html_link(html)
        assert result == "/api/document.anml"

    def test_discover_html_link_href_first(self) -> None:
        """Find ANML URL when href comes before rel."""
        html = '<html><head><link href="/api.anml" rel="anml"></head></html>'
        result = discover_html_link(html)
        assert result == "/api.anml"

    def test_discover_html_link_not_found(self) -> None:
        """Return None when no ANML link in HTML."""
        html = '<html><head><link rel="stylesheet" href="/style.css"></head></html>'
        result = discover_html_link(html)
        assert result is None

    def test_discover_html_link_single_quotes(self) -> None:
        """Handle single-quoted attributes."""
        html = "<html><head><link rel='anml' href='/api.anml'></head></html>"
        result = discover_html_link(html)
        assert result == "/api.anml"

    def test_discover_html_link_empty_html(self) -> None:
        """Return None for empty HTML."""
        result = discover_html_link("")
        assert result is None
