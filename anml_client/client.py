"""Main AnmlClient with builder pattern."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import httpx

from anml_client.action import execute_action as _execute_action
from anml_client.action import find_action
from anml_client.config import (
    AllowAllTrustPolicy,
    ClientConfig,
    RetryPolicy,
    TimeoutConfig,
    TrustPolicy,
)
from anml_client.discovery import discover as _discover
from anml_client.errors import (
    ActionExecutionError,
    AnmlTimeoutError,
    TransportInsecureError,
    TrustDeniedError,
)
from anml_client.middleware import MiddlewareChain
from anml_client.pagination import paginate as _paginate
from anml_client.parser import parse_anml
from anml_client.types import AnmlDocument


class AnmlClient:
    """ANML 1.0 client for fetching and interacting with ANML documents."""

    def __init__(self, config: ClientConfig, http_client: httpx.AsyncClient | None = None) -> None:
        """Initialize the ANML client.

        Args:
            config: Client configuration.
            http_client: Optional pre-configured httpx client.
        """
        self._config = config
        self._middleware = MiddlewareChain()
        self._http_client = http_client or self._build_http_client()

    def _build_http_client(self) -> httpx.AsyncClient:
        """Build an httpx AsyncClient from config."""
        timeout = httpx.Timeout(
            connect=self._config.timeout.connect,
            read=self._config.timeout.read,
            write=self._config.timeout.write,
            pool=self._config.timeout.pool,
        )
        headers = {
            "user-agent": self._config.user_agent,
            "accept": "application/anml+xml, application/anml+json, application/xml, application/json",
            **self._config.default_headers,
        }
        return httpx.AsyncClient(
            timeout=timeout,
            headers=headers,
            follow_redirects=True,
            max_redirects=self._config.max_redirects,
        )

    @classmethod
    def builder(cls) -> AnmlClientBuilder:
        """Create a new client builder.

        Returns:
            An AnmlClientBuilder instance.
        """
        return AnmlClientBuilder()

    def _validate_url(self, url: str) -> None:
        """Validate URL against security policies.

        Args:
            url: The URL to validate.

        Raises:
            TransportInsecureError: If HTTPS is required but URL is not HTTPS.
            TrustDeniedError: If the URL is not trusted.
        """
        if self._config.require_https and not url.startswith("https://"):
            raise TransportInsecureError(
                f"HTTPS required but got: {url}. "
                "Set require_https=False to allow insecure connections."
            )
        if not self._config.trust_policy.is_trusted(url):
            raise TrustDeniedError(f"URL not trusted by policy: {url}")

    async def fetch_url(self, url: str) -> AnmlDocument:
        """Fetch and parse an ANML document from a URL.

        Args:
            url: The full URL to fetch.

        Returns:
            Parsed AnmlDocument.

        Raises:
            TransportInsecureError: If HTTPS is required but URL is not HTTPS.
            TrustDeniedError: If the URL is not trusted.
            AnmlTimeoutError: If the request times out.
        """
        self._validate_url(url)

        try:
            response = await self._http_client.get(url)
            response.raise_for_status()
        except httpx.TimeoutException as e:
            raise AnmlTimeoutError(f"Request timed out: {url}") from e
        except httpx.HTTPError as e:
            raise ActionExecutionError(f"HTTP error fetching {url}: {e}") from e

        content_type = response.headers.get("content-type", "application/anml+xml")
        return parse_anml(response.text, content_type)

    async def fetch(self, path: str) -> AnmlDocument:
        """Fetch and parse an ANML document from a relative path.

        Args:
            path: Relative path (appended to base_url).

        Returns:
            Parsed AnmlDocument.
        """
        base = self._config.base_url.rstrip("/")
        url = f"{base}/{path.lstrip('/')}"
        return await self.fetch_url(url)

    async def discover(self, base_url: str) -> str | None:
        """Discover the ANML document URL for a given base URL.

        Args:
            base_url: The base URL to discover from.

        Returns:
            The ANML document URL if found, None otherwise.
        """
        return await _discover(self._http_client, base_url)

    async def execute_action(
        self,
        doc: AnmlDocument,
        action_id: str,
        params: dict[str, Any] | None = None,
        auth_headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Execute an action from an ANML document.

        Args:
            doc: The ANML document containing the action.
            action_id: The ID of the action to execute.
            params: Parameters to bind to the action.
            auth_headers: Additional authentication headers.

        Returns:
            The HTTP response.

        Raises:
            ActionExecutionError: If the action is not found or execution fails.
        """
        action = find_action(doc, action_id)
        if action is None:
            raise ActionExecutionError(f"Action not found: {action_id}")

        if action.url:
            self._validate_url(action.url)

        return await _execute_action(self._http_client, action, params, auth_headers)

    async def paginate(self, doc: AnmlDocument) -> AsyncGenerator[AnmlDocument, None]:
        """Async iterate over paginated ANML documents.

        Args:
            doc: The initial ANML document.

        Yields:
            Each subsequent ANML document.
        """
        async for page in _paginate(self._http_client, doc):
            yield page

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._http_client.aclose()

    async def __aenter__(self) -> AnmlClient:
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""
        await self.close()


class AnmlClientBuilder:
    """Builder for constructing AnmlClient instances."""

    def __init__(self) -> None:
        self._config = ClientConfig()
        self._http_client: httpx.AsyncClient | None = None

    def base_url(self, url: str) -> AnmlClientBuilder:
        """Set the base URL.

        Args:
            url: The base URL for relative path resolution.

        Returns:
            Self for chaining.
        """
        self._config.base_url = url
        return self

    def trust_policy(self, policy: TrustPolicy) -> AnmlClientBuilder:
        """Set the trust policy.

        Args:
            policy: The trust policy to use.

        Returns:
            Self for chaining.
        """
        self._config.trust_policy = policy
        return self

    def timeout(self, timeout: TimeoutConfig) -> AnmlClientBuilder:
        """Set timeout configuration.

        Args:
            timeout: The timeout configuration.

        Returns:
            Self for chaining.
        """
        self._config.timeout = timeout
        return self

    def retry(self, retry: RetryPolicy) -> AnmlClientBuilder:
        """Set retry policy.

        Args:
            retry: The retry policy.

        Returns:
            Self for chaining.
        """
        self._config.retry = retry
        return self

    def require_https(self, require: bool) -> AnmlClientBuilder:
        """Set whether HTTPS is required.

        Args:
            require: Whether to require HTTPS.

        Returns:
            Self for chaining.
        """
        self._config.require_https = require
        return self

    def user_agent(self, ua: str) -> AnmlClientBuilder:
        """Set the User-Agent header.

        Args:
            ua: The User-Agent string.

        Returns:
            Self for chaining.
        """
        self._config.user_agent = ua
        return self

    def headers(self, headers: dict[str, str]) -> AnmlClientBuilder:
        """Set default headers.

        Args:
            headers: Default headers to include in all requests.

        Returns:
            Self for chaining.
        """
        self._config.default_headers = headers
        return self

    def http_client(self, client: httpx.AsyncClient) -> AnmlClientBuilder:
        """Set a pre-configured httpx client.

        Args:
            client: The httpx AsyncClient to use.

        Returns:
            Self for chaining.
        """
        self._http_client = client
        return self

    def build(self) -> AnmlClient:
        """Build the AnmlClient.

        Returns:
            A configured AnmlClient instance.
        """
        return AnmlClient(self._config, self._http_client)
