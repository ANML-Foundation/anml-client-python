"""Tests for ANML parser."""

import pytest

from anml_client.errors import ParseError
from anml_client.parser import parse_anml, parse_anml_json, parse_anml_xml
from anml_client.types import (
    Confidentiality,
    DisclosureRequirement,
    HttpMethod,
    ParamType,
    StepStatus,
    UsageRight,
)


class TestParseAnmlXml:
    """Tests for XML parsing."""

    def test_parse_basic_document(self, sample_xml: str) -> None:
        """Parse a complete ANML XML document."""
        doc = parse_anml_xml(sample_xml)
        assert doc.version == "1.0"

    def test_parse_head(self, sample_xml: str) -> None:
        """Parse head section with title, meta, constraints."""
        doc = parse_anml_xml(sample_xml)
        assert doc.head.title is not None
        assert doc.head.title.text == "Test Document"
        assert len(doc.head.meta) == 2
        assert doc.head.meta[0].name == "author"
        assert doc.head.meta[0].content == "Test Author"

    def test_parse_constraints(self, sample_xml: str) -> None:
        """Parse constraints element."""
        doc = parse_anml_xml(sample_xml)
        assert doc.head.constraints is not None
        assert doc.head.constraints.max_requests_per_minute == 60
        assert doc.head.constraints.max_depth == 3
        assert "example.com" in doc.head.constraints.allowed_domains
        assert "evil.com" in doc.head.constraints.denied_domains

    def test_parse_disclosures(self, sample_xml: str) -> None:
        """Parse disclosure elements."""
        doc = parse_anml_xml(sample_xml)
        assert len(doc.head.disclosures) == 2
        assert doc.head.disclosures[0].field == "email"
        assert doc.head.disclosures[0].requirement == DisclosureRequirement.CONSENT
        assert doc.head.disclosures[0].purpose == "communication"
        assert doc.head.disclosures[1].requirement == DisclosureRequirement.INFORM

    def test_parse_rights(self, sample_xml: str) -> None:
        """Parse rights element."""
        doc = parse_anml_xml(sample_xml)
        assert doc.head.rights is not None
        assert UsageRight.READ in doc.head.rights.usage
        assert UsageRight.CACHE in doc.head.rights.usage
        assert doc.head.rights.confidentiality == Confidentiality.INTERNAL
        assert doc.head.rights.attribution == "Test Corp"

    def test_parse_persona(self, sample_xml: str) -> None:
        """Parse persona element."""
        doc = parse_anml_xml(sample_xml)
        assert doc.persona is not None
        assert doc.persona.name == "Helper"
        assert doc.persona.role == "assistant"
        assert doc.persona.tone is not None
        assert doc.persona.tone.style == "friendly"
        assert doc.persona.tone.formality == "casual"

    def test_parse_state_and_flow(self, sample_xml: str) -> None:
        """Parse state with flows and steps."""
        doc = parse_anml_xml(sample_xml)
        assert doc.state is not None
        assert len(doc.state.flows) == 1
        flow = doc.state.flows[0]
        assert flow.id == "onboarding"
        assert len(flow.steps) == 3
        assert flow.steps[0].status == StepStatus.COMPLETE
        assert flow.steps[1].status == StepStatus.ACTIVE
        assert flow.steps[2].status == StepStatus.PENDING

    def test_parse_step_context(self, sample_xml: str) -> None:
        """Parse step context elements."""
        doc = parse_anml_xml(sample_xml)
        assert doc.state is not None
        step = doc.state.flows[0].steps[1]
        assert len(step.context) == 1
        assert step.context[0].key == "user_name"
        assert step.context[0].value == "Alice"

    def test_parse_actions(self, sample_xml: str) -> None:
        """Parse interact section with actions."""
        doc = parse_anml_xml(sample_xml)
        assert doc.interact is not None
        assert len(doc.interact.actions) == 2

        action = doc.interact.actions[0]
        assert action.id == "get-profile"
        assert action.method == HttpMethod.GET
        assert "profile" in action.url
        assert len(action.params) == 1
        assert action.params[0].name == "user_id"
        assert action.params[0].type == ParamType.STRING
        assert action.params[0].required is True

    def test_parse_action_with_body_template(self, sample_xml: str) -> None:
        """Parse action with headers and body template."""
        doc = parse_anml_xml(sample_xml)
        assert doc.interact is not None
        action = doc.interact.actions[1]
        assert action.id == "update-name"
        assert action.method == HttpMethod.POST
        assert action.headers.get("Content-Type") == "application/json"
        assert "name" in action.body_template

    def test_parse_knowledge(self, sample_xml: str) -> None:
        """Parse knowledge section."""
        doc = parse_anml_xml(sample_xml)
        assert doc.knowledge is not None
        assert len(doc.knowledge.informs) == 2
        assert doc.knowledge.informs[0].key == "greeting"
        assert "welcome" in doc.knowledge.informs[0].value.lower()

        assert len(doc.knowledge.asks) == 1
        ask = doc.knowledge.asks[0]
        assert ask.key == "preferred_language"
        assert ask.required is True
        assert len(ask.options) == 3

    def test_parse_body(self, sample_xml: str) -> None:
        """Parse body section."""
        doc = parse_anml_xml(sample_xml)
        assert doc.body is not None
        assert "main content" in doc.body.content
        assert len(doc.body.media) == 1
        assert doc.body.media[0].type == "image/png"
        assert doc.body.media[0].integrity == "sha256-abc123"

    def test_parse_nav(self, sample_xml: str) -> None:
        """Parse nav section."""
        doc = parse_anml_xml(sample_xml)
        assert doc.nav is not None
        assert doc.nav.next == "https://example.com/page2"
        assert doc.nav.prev == "https://example.com/page0"
        assert len(doc.nav.related) == 2

    def test_parse_minimal_document(self, minimal_xml: str) -> None:
        """Parse a minimal ANML document."""
        doc = parse_anml_xml(minimal_xml)
        assert doc.version == "1.0"
        assert doc.head.title is not None
        assert doc.head.title.text == "Minimal"
        assert doc.persona is None
        assert doc.state is None
        assert doc.interact is None

    def test_parse_invalid_xml(self) -> None:
        """Raise ParseError on invalid XML."""
        with pytest.raises(ParseError):
            parse_anml_xml("not xml at all")

    def test_parse_empty_string(self) -> None:
        """Raise ParseError on empty string."""
        with pytest.raises(ParseError):
            parse_anml_xml("")


class TestParseAnmlJson:
    """Tests for JSON parsing."""

    def test_parse_basic_json(self, sample_json: str) -> None:
        """Parse a complete ANML JSON document."""
        doc = parse_anml_json(sample_json)
        assert doc.version == "1.0"
        assert doc.head.title is not None
        assert doc.head.title.text == "JSON Test Document"

    def test_parse_json_persona(self, sample_json: str) -> None:
        """Parse persona from JSON."""
        doc = parse_anml_json(sample_json)
        assert doc.persona is not None
        assert doc.persona.name == "Bot"

    def test_parse_json_state(self, sample_json: str) -> None:
        """Parse state from JSON."""
        doc = parse_anml_json(sample_json)
        assert doc.state is not None
        assert len(doc.state.flows) == 1
        assert doc.state.flows[0].steps[0].status == StepStatus.ACTIVE

    def test_parse_json_actions(self, sample_json: str) -> None:
        """Parse actions from JSON."""
        doc = parse_anml_json(sample_json)
        assert doc.interact is not None
        assert doc.interact.actions[0].id == "search"
        assert doc.interact.actions[0].method == HttpMethod.GET

    def test_parse_json_knowledge(self, sample_json: str) -> None:
        """Parse knowledge from JSON."""
        doc = parse_anml_json(sample_json)
        assert doc.knowledge is not None
        assert len(doc.knowledge.informs) == 1
        assert len(doc.knowledge.asks) == 1
        assert doc.knowledge.asks[0].required is True

    def test_parse_json_nav(self, sample_json: str) -> None:
        """Parse nav from JSON."""
        doc = parse_anml_json(sample_json)
        assert doc.nav is not None
        assert doc.nav.next == "https://example.com/next"

    def test_parse_invalid_json(self) -> None:
        """Raise ParseError on invalid JSON."""
        with pytest.raises(ParseError):
            parse_anml_json("{invalid json")

    def test_parse_empty_json(self) -> None:
        """Raise ParseError on empty string."""
        with pytest.raises(ParseError):
            parse_anml_json("")


class TestParseAnml:
    """Tests for content-type based parsing."""

    def test_parse_xml_content_type(self, sample_xml: str) -> None:
        """Route to XML parser based on content type."""
        doc = parse_anml(sample_xml, "application/anml+xml")
        assert doc.version == "1.0"

    def test_parse_json_content_type(self, sample_json: str) -> None:
        """Route to JSON parser based on content type."""
        doc = parse_anml(sample_json, "application/anml+json")
        assert doc.version == "1.0"

    def test_parse_xml_with_charset(self, sample_xml: str) -> None:
        """Handle content type with charset parameter."""
        doc = parse_anml(sample_xml, "application/xml; charset=utf-8")
        assert doc.version == "1.0"

    def test_parse_auto_detect_xml(self, sample_xml: str) -> None:
        """Auto-detect XML when content type is unknown."""
        doc = parse_anml(sample_xml, "application/octet-stream")
        assert doc.version == "1.0"

    def test_parse_auto_detect_json(self, sample_json: str) -> None:
        """Auto-detect JSON when content type is unknown."""
        doc = parse_anml(sample_json, "application/octet-stream")
        assert doc.version == "1.0"
