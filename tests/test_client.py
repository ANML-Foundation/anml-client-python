"""Tests for the AnmlClient."""

import pytest
import httpx

from anml_client.client import AnmlClient, AnmlClientBuilder
from anml_client.config import (
    AllowAllTrustPolicy,
    AllowListTrustPolicy,
    ClientConfig,
    DenyAllTrustPolicy,
    TimeoutConfig,
)
from anml_client.errors import TransportInsecureError, TrustDeniedError
from anml_client.flow import FlowNavigator, get_current_step, get_next_step, is_flow_complete
from anml_client.integrity import compute_sri, verify_sri
from anml_client.knowledge import get_asks, get_informs, get_required_asks
from anml_client.parser import parse_anml_xml
from anml_client.types import StepStatus

from tests.conftest import SAMPLE_ANML_XML


class TestAnmlClientBuilder:
    """Tests for the builder pattern."""

    def test_build_default(self) -> None:
        """Build client with defaults."""
        client = AnmlClient.builder().require_https(False).build()
        assert client is not None

    def test_build_with_base_url(self) -> None:
        """Build client with base URL."""
        client = (
            AnmlClient.builder()
            .base_url("https://api.example.com")
            .build()
        )
        assert client._config.base_url == "https://api.example.com"

    def test_build_with_trust_policy(self) -> None:
        """Build client with custom trust policy."""
        policy = AllowListTrustPolicy(["example.com"])
        client = AnmlClient.builder().trust_policy(policy).build()
        assert client._config.trust_policy is policy

    def test_build_with_timeout(self) -> None:
        """Build client with custom timeout."""
        timeout = TimeoutConfig(connect=10.0, read=60.0)
        client = AnmlClient.builder().timeout(timeout).build()
        assert client._config.timeout.connect == 10.0
        assert client._config.timeout.read == 60.0

    def test_build_with_user_agent(self) -> None:
        """Build client with custom user agent."""
        client = AnmlClient.builder().user_agent("my-agent/1.0").build()
        assert client._config.user_agent == "my-agent/1.0"

    def test_build_chaining(self) -> None:
        """Builder methods return self for chaining."""
        builder = AnmlClient.builder()
        result = (
            builder.base_url("https://example.com")
            .require_https(True)
            .user_agent("test/1.0")
        )
        assert result is builder


class TestAnmlClientValidation:
    """Tests for URL validation."""

    def test_reject_http_when_https_required(self) -> None:
        """Reject HTTP URLs when HTTPS is required."""
        client = AnmlClient.builder().require_https(True).build()
        with pytest.raises(TransportInsecureError):
            client._validate_url("http://example.com/api")

    def test_allow_https(self) -> None:
        """Allow HTTPS URLs."""
        client = AnmlClient.builder().require_https(True).build()
        client._validate_url("https://example.com/api")  # Should not raise

    def test_allow_http_when_not_required(self) -> None:
        """Allow HTTP when HTTPS not required."""
        client = AnmlClient.builder().require_https(False).build()
        client._validate_url("http://example.com/api")  # Should not raise

    def test_reject_untrusted_domain(self) -> None:
        """Reject URLs from untrusted domains."""
        policy = AllowListTrustPolicy(["trusted.com"])
        client = AnmlClient.builder().trust_policy(policy).build()
        with pytest.raises(TrustDeniedError):
            client._validate_url("https://untrusted.com/api")

    def test_allow_trusted_domain(self) -> None:
        """Allow URLs from trusted domains."""
        policy = AllowListTrustPolicy(["example.com"])
        client = AnmlClient.builder().trust_policy(policy).build()
        client._validate_url("https://example.com/api")  # Should not raise


class TestFlowNavigation:
    """Tests for flow navigation utilities."""

    def test_get_current_step(self) -> None:
        """Get the active step."""
        doc = parse_anml_xml(SAMPLE_ANML_XML)
        step = get_current_step(doc)
        assert step is not None
        assert step.id == "step-2"
        assert step.status == StepStatus.ACTIVE

    def test_get_next_step(self) -> None:
        """Get the next pending step."""
        doc = parse_anml_xml(SAMPLE_ANML_XML)
        step = get_next_step(doc)
        assert step is not None
        assert step.id == "step-3"
        assert step.status == StepStatus.PENDING

    def test_is_flow_not_complete(self) -> None:
        """Flow with pending steps is not complete."""
        doc = parse_anml_xml(SAMPLE_ANML_XML)
        assert is_flow_complete(doc) is False

    def test_flow_navigator(self) -> None:
        """FlowNavigator provides convenient access."""
        doc = parse_anml_xml(SAMPLE_ANML_XML)
        nav = FlowNavigator(doc)
        assert nav.current_step is not None
        assert nav.current_step.id == "step-2"
        assert nav.next_step is not None
        assert nav.is_complete is False
        assert len(nav.get_completed_steps()) == 1
        assert len(nav.get_pending_steps()) == 1

    def test_flow_navigator_find_step(self) -> None:
        """Find step by ID."""
        doc = parse_anml_xml(SAMPLE_ANML_XML)
        nav = FlowNavigator(doc)
        step = nav.get_step_by_id("step-1")
        assert step is not None
        assert step.label == "Welcome"


class TestKnowledge:
    """Tests for knowledge helpers."""

    def test_get_informs(self) -> None:
        """Get inform elements."""
        doc = parse_anml_xml(SAMPLE_ANML_XML)
        informs = get_informs(doc)
        assert len(informs) == 2
        assert informs[0].key == "greeting"

    def test_get_asks(self) -> None:
        """Get ask elements."""
        doc = parse_anml_xml(SAMPLE_ANML_XML)
        asks = get_asks(doc)
        assert len(asks) == 1
        assert asks[0].key == "preferred_language"

    def test_get_required_asks(self) -> None:
        """Get required ask elements."""
        doc = parse_anml_xml(SAMPLE_ANML_XML)
        required = get_required_asks(doc)
        assert len(required) == 1
        assert required[0].required is True


class TestIntegrity:
    """Tests for SRI verification."""

    def test_compute_sri_sha256(self) -> None:
        """Compute SHA-256 SRI hash."""
        data = b"hello world"
        sri = compute_sri(data, "sha256")
        assert sri.startswith("sha256-")
        assert len(sri) > 10

    def test_verify_sri_valid(self) -> None:
        """Verify valid SRI hash."""
        data = b"hello world"
        sri = compute_sri(data, "sha256")
        assert verify_sri(data, sri) is True

    def test_verify_sri_invalid(self) -> None:
        """Verify invalid SRI hash."""
        data = b"hello world"
        sri = compute_sri(b"different data", "sha256")
        assert verify_sri(data, sri) is False

    def test_compute_sri_sha384(self) -> None:
        """Compute SHA-384 SRI hash."""
        data = b"test data"
        sri = compute_sri(data, "sha384")
        assert sri.startswith("sha384-")

    def test_compute_sri_sha512(self) -> None:
        """Compute SHA-512 SRI hash."""
        data = b"test data"
        sri = compute_sri(data, "sha512")
        assert sri.startswith("sha512-")

    def test_verify_roundtrip(self) -> None:
        """Compute and verify roundtrip for all algorithms."""
        data = b"roundtrip test"
        for alg in ("sha256", "sha384", "sha512"):
            sri = compute_sri(data, alg)
            assert verify_sri(data, sri) is True
