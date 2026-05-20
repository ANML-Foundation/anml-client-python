"""Tests for disclosure evaluation and consent store."""

import pytest

from anml_client.config import AllowAllTrustPolicy, DenyAllTrustPolicy
from anml_client.disclosure import ConsentStore, DisclosureResult, evaluate_disclosure
from anml_client.types import AnmlDisclosure, DisclosureRequirement


class TestConsentStore:
    """Tests for the ConsentStore."""

    def test_grant_consent(self) -> None:
        """Grant consent for a field."""
        store = ConsentStore()
        store.grant("email", purpose="communication")
        assert store.check("email") is True

    def test_revoke_consent(self) -> None:
        """Revoke consent for a field."""
        store = ConsentStore()
        store.grant("email")
        store.revoke("email")
        assert store.check("email") is False

    def test_check_unknown_field(self) -> None:
        """Return None for unknown field."""
        store = ConsentStore()
        assert store.check("unknown") is None

    def test_clear_all(self) -> None:
        """Clear all consent records."""
        store = ConsentStore()
        store.grant("email")
        store.grant("name")
        store.clear()
        assert store.check("email") is None
        assert store.check("name") is None

    def test_grant_overrides_revoke(self) -> None:
        """Later grant overrides earlier revoke."""
        store = ConsentStore()
        store.revoke("email")
        store.grant("email")
        assert store.check("email") is True


class TestEvaluateDisclosure:
    """Tests for disclosure evaluation."""

    def test_no_requirement(self) -> None:
        """No requirement means allowed."""
        disclosure = AnmlDisclosure(field="data", requirement=DisclosureRequirement.NONE)
        store = ConsentStore()
        policy = AllowAllTrustPolicy()
        result = evaluate_disclosure(disclosure, store, policy)
        assert result == DisclosureResult.ALLOWED

    def test_inform_requirement(self) -> None:
        """Inform requirement returns informed."""
        disclosure = AnmlDisclosure(field="data", requirement=DisclosureRequirement.INFORM)
        store = ConsentStore()
        policy = AllowAllTrustPolicy()
        result = evaluate_disclosure(disclosure, store, policy)
        assert result == DisclosureResult.INFORMED

    def test_consent_granted(self) -> None:
        """Consent requirement with grant returns allowed."""
        disclosure = AnmlDisclosure(field="email", requirement=DisclosureRequirement.CONSENT)
        store = ConsentStore()
        store.grant("email")
        policy = AllowAllTrustPolicy()
        result = evaluate_disclosure(disclosure, store, policy)
        assert result == DisclosureResult.ALLOWED

    def test_consent_not_granted(self) -> None:
        """Consent requirement without grant returns consent_required."""
        disclosure = AnmlDisclosure(field="email", requirement=DisclosureRequirement.CONSENT)
        store = ConsentStore()
        policy = AllowAllTrustPolicy()
        result = evaluate_disclosure(disclosure, store, policy)
        assert result == DisclosureResult.CONSENT_REQUIRED

    def test_consent_revoked(self) -> None:
        """Consent requirement with revoke returns denied."""
        disclosure = AnmlDisclosure(field="email", requirement=DisclosureRequirement.CONSENT)
        store = ConsentStore()
        store.revoke("email")
        policy = AllowAllTrustPolicy()
        result = evaluate_disclosure(disclosure, store, policy)
        assert result == DisclosureResult.DENIED

    def test_untrusted_url_denied(self) -> None:
        """Untrusted URL returns denied regardless of consent."""
        disclosure = AnmlDisclosure(field="email", requirement=DisclosureRequirement.CONSENT)
        store = ConsentStore()
        store.grant("email")
        policy = DenyAllTrustPolicy()
        result = evaluate_disclosure(disclosure, store, policy, url="https://evil.com")
        assert result == DisclosureResult.DENIED

    def test_explicit_consent_required(self) -> None:
        """Explicit consent requirement without grant returns consent_required."""
        disclosure = AnmlDisclosure(
            field="ssn", requirement=DisclosureRequirement.EXPLICIT_CONSENT
        )
        store = ConsentStore()
        policy = AllowAllTrustPolicy()
        result = evaluate_disclosure(disclosure, store, policy)
        assert result == DisclosureResult.CONSENT_REQUIRED
