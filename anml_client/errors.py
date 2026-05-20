"""Exception hierarchy for the ANML client library."""


class AnmlClientError(Exception):
    """Base exception for all ANML client errors."""


class TransportInsecureError(AnmlClientError):
    """Raised when a non-HTTPS transport is used without explicit opt-in."""


class ParseError(AnmlClientError):
    """Raised when an ANML document cannot be parsed."""


class DiscoveryError(AnmlClientError):
    """Raised when ANML discovery fails."""


class TrustDeniedError(AnmlClientError):
    """Raised when a trust policy denies a request."""


class DisclosureViolationError(AnmlClientError):
    """Raised when a disclosure requirement is violated."""


class ActionExecutionError(AnmlClientError):
    """Raised when an action cannot be executed."""


class AnmlTimeoutError(AnmlClientError):
    """Raised when a request times out."""


class CircuitBreakerOpenError(AnmlClientError):
    """Raised when the circuit breaker is open."""


class UnsupportedExtensionError(AnmlClientError):
    """Raised when an unsupported extension is encountered."""


class SriVerificationError(AnmlClientError):
    """Raised when SRI verification fails."""
