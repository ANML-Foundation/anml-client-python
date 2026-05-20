"""Shared test fixtures."""

import pytest


SAMPLE_ANML_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<anml version="1.0">
  <head>
    <title>Test Document</title>
    <meta name="author" content="Test Author"/>
    <meta name="description" content="A test ANML document"/>
    <constraints max-requests-per-minute="60" max-depth="3">
      <allowed-domain>example.com</allowed-domain>
      <denied-domain>evil.com</denied-domain>
    </constraints>
    <disclosure field="email" requirement="consent" purpose="communication" retention="30d"/>
    <disclosure field="name" requirement="inform" purpose="personalization"/>
    <rights usage="read,cache" confidentiality="internal" attribution="Test Corp" license="MIT"/>
  </head>
  <persona name="Helper" role="assistant">
    <tone style="friendly" formality="casual"/>
  </persona>
  <state>
    <flow id="onboarding">
      <step id="step-1" label="Welcome" status="complete" next="step-2"/>
      <step id="step-2" label="Setup" status="active" next="step-3">
        <context key="user_name" value="Alice" source="input"/>
      </step>
      <step id="step-3" label="Done" status="pending"/>
    </flow>
  </state>
  <interact>
    <action id="get-profile" method="GET" url="https://api.example.com/profile/{user_id}" description="Get user profile">
      <param name="user_id" type="string" required="true" description="The user ID"/>
    </action>
    <action id="update-name" method="POST" url="https://api.example.com/profile" description="Update name">
      <param name="name" type="string" required="true"/>
      <header name="Content-Type" value="application/json"/>
      <body-template>{"name": "{name}"}</body-template>
    </action>
  </interact>
  <knowledge>
    <inform key="greeting" format="text">Hello, welcome to the system!</inform>
    <inform key="version" format="text">1.0.0</inform>
    <ask key="preferred_language" prompt="What language do you prefer?" type="string" required="true">
      <option>English</option>
      <option>Spanish</option>
      <option>French</option>
    </ask>
  </knowledge>
  <body>
    <content>This is the main content of the document.</content>
    <media type="image/png" src="https://example.com/logo.png" alt="Logo" integrity="sha256-abc123"/>
  </body>
  <nav next="https://example.com/page2" prev="https://example.com/page0" first="https://example.com/page1" last="https://example.com/page10">
    <related href="https://example.com/related1"/>
    <related href="https://example.com/related2"/>
  </nav>
</anml>
"""

SAMPLE_ANML_JSON = """\
{
  "version": "1.0",
  "head": {
    "title": {"text": "JSON Test Document"},
    "meta": [
      {"name": "author", "content": "JSON Author"}
    ],
    "disclosures": [
      {"field": "email", "requirement": "consent", "purpose": "contact"}
    ]
  },
  "persona": {
    "name": "Bot",
    "role": "helper"
  },
  "state": {
    "flows": [
      {
        "id": "main",
        "steps": [
          {"id": "s1", "label": "Start", "status": "active"},
          {"id": "s2", "label": "End", "status": "pending"}
        ]
      }
    ]
  },
  "interact": {
    "actions": [
      {
        "id": "search",
        "method": "GET",
        "url": "https://api.example.com/search",
        "params": [
          {"name": "q", "type": "string", "required": true}
        ]
      }
    ]
  },
  "knowledge": {
    "informs": [
      {"key": "info", "value": "Some information", "format": "text"}
    ],
    "asks": [
      {"key": "name", "prompt": "What is your name?", "type": "string", "required": true}
    ]
  },
  "body": {
    "content": "JSON body content"
  },
  "nav": {
    "next": "https://example.com/next"
  }
}
"""


MINIMAL_ANML_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<anml version="1.0">
  <head>
    <title>Minimal</title>
  </head>
</anml>
"""


@pytest.fixture
def sample_xml() -> str:
    """Return sample ANML XML."""
    return SAMPLE_ANML_XML


@pytest.fixture
def sample_json() -> str:
    """Return sample ANML JSON."""
    return SAMPLE_ANML_JSON


@pytest.fixture
def minimal_xml() -> str:
    """Return minimal ANML XML."""
    return MINIMAL_ANML_XML
