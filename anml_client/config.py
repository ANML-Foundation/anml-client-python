"""Client configuration, trust policies, and retry settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@runtime_checkable
class TrustPolicy(Protocol):
    """Protocol for trust policy implementations."""

    def is_trusted(self, url: str) -> bool:
        """Check if a URL is trusted by this policy."""
        ...


class AllowAllTrustPolicy:
    """Trust policy that allows all URLs."""

    def is_trusted(self, url: str) -> bool:
        """All URLs are trusted."""
        return True


class DenyAllTrustPolicy:
    """Trust policy that denies all URLs."""

    def is_trusted(self, url: str) -> bool:
        """No URLs are trusted."""
        return False


class AllowListTrustPolicy:
    """Trust policy that allows only URLs matching a list of domain patterns."""

    def __init__(self, allowed_domains: list[str]) -> None:
        self._allowed_domains = allowed_domains

    def is_trusted(self, url: str) -> bool:
        """Check if URL domain is in the allow list."""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        return any(
            hostname == domain or hostname.endswith(f".{domain}")
            for domain in self._allowed_domains
        )


@dataclass
class TimeoutConfig:
    """Timeout configuration for HTTP requests."""

    connect: float = 5.0
    read: float = 30.0
    write: float = 30.0
    pool: float = 5.0

    @property
    def as_httpx_timeout(self) -> tuple[float, float, float, float]:
        """Return as httpx timeout tuple (connect, read, write, pool)."""
        return (self.connect, self.read, self.write, self.pool)


@dataclass
class RetryPolicy:
    """Retry policy for failed requests."""

    max_retries: int = 3
    backoff_factor: float = 0.5
    retry_on_status: list[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])


@dataclass
class ClientConfig:
    """Configuration for the ANML client."""

    base_url: str = ""
    trust_policy: TrustPolicy = field(default_factory=AllowAllTrustPolicy)
    timeout: TimeoutConfig = field(default_factory=TimeoutConfig)
    retry: RetryPolicy = field(default_factory=RetryPolicy)
    require_https: bool = True
    user_agent: str = "anml-client-python/0.1.0"
    default_headers: dict[str, str] = field(default_factory=dict)
    max_redirects: int = 10
