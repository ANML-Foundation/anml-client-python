"""Disclosure evaluation and consent management."""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum

from anml_client.config import TrustPolicy
from anml_client.errors import DisclosureViolationError
from anml_client.types import AnmlDisclosure, AnmlDocument, DisclosureRequirement


class DisclosureResult(str, Enum):
    """Result of disclosure evaluation."""

    ALLOWED = "allowed"
    DENIED = "denied"
    CONSENT_REQUIRED = "consent_required"
    INFORMED = "informed"


@dataclass
class ConsentRecord:
    """Record of a consent decision."""

    field: str
    granted: bool
    purpose: str = ""
    timestamp: float = 0.0


class ConsentStore:
    """In-memory consent store for tracking disclosure decisions."""

    def __init__(self) -> None:
        self._consents: dict[str, ConsentRecord] = {}

    def grant(self, field_name: str, purpose: str = "") -> None:
        """Grant consent for a field.

        Args:
            field_name: The field to grant consent for.
            purpose: The purpose of the consent.
        """
        self._consents[field_name] = ConsentRecord(
            field=field_name,
            granted=True,
            purpose=purpose,
            timestamp=time.time(),
        )

    def revoke(self, field_name: str) -> None:
        """Revoke consent for a field.

        Args:
            field_name: The field to revoke consent for.
        """
        self._consents[field_name] = ConsentRecord(
            field=field_name,
            granted=False,
            timestamp=time.time(),
        )

    def check(self, field_name: str) -> bool | None:
        """Check if consent has been granted for a field.

        Args:
            field_name: The field to check.

        Returns:
            True if granted, False if revoked, None if no decision recorded.
        """
        record = self._consents.get(field_name)
        if record is None:
            return None
        return record.granted

    def clear(self) -> None:
        """Clear all consent records."""
        self._consents.clear()


def evaluate_disclosure(
    disclosure: AnmlDisclosure,
    consent_store: ConsentStore,
    trust_policy: TrustPolicy,
    url: str = "",
) -> DisclosureResult:
    """Evaluate a disclosure requirement against consent and trust.

    Args:
        disclosure: The disclosure to evaluate.
        consent_store: The consent store to check.
        trust_policy: The trust policy to apply.
        url: The URL context for trust evaluation.

    Returns:
        The disclosure evaluation result.
    """
    # If URL is provided and not trusted, deny
    if url and not trust_policy.is_trusted(url):
        return DisclosureResult.DENIED

    requirement = disclosure.requirement

    if requirement == DisclosureRequirement.NONE:
        return DisclosureResult.ALLOWED

    if requirement == DisclosureRequirement.INFORM:
        return DisclosureResult.INFORMED

    # For consent and explicit-consent, check the consent store
    consent = consent_store.check(disclosure.field)
    if consent is True:
        return DisclosureResult.ALLOWED
    elif consent is False:
        return DisclosureResult.DENIED
    else:
        return DisclosureResult.CONSENT_REQUIRED


def evaluate_all_disclosures(
    doc: AnmlDocument,
    consent_store: ConsentStore,
    trust_policy: TrustPolicy,
    url: str = "",
) -> dict[str, DisclosureResult]:
    """Evaluate all disclosures in a document.

    Args:
        doc: The ANML document.
        consent_store: The consent store.
        trust_policy: The trust policy.
        url: The URL context.

    Returns:
        Mapping of field names to disclosure results.

    Raises:
        DisclosureViolationError: If any disclosure is denied.
    """
    results: dict[str, DisclosureResult] = {}
    for disclosure in doc.head.disclosures:
        result = evaluate_disclosure(disclosure, consent_store, trust_policy, url)
        results[disclosure.field] = result
        if result == DisclosureResult.DENIED:
            raise DisclosureViolationError(
                f"Disclosure denied for field '{disclosure.field}': "
                f"purpose='{disclosure.purpose}'"
            )
    return results
