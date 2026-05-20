"""Pydantic models for ANML 1.0 documents."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class StepStatus(str, Enum):
    """Status of a flow step."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"
    SKIPPED = "skipped"
    FAILED = "failed"


class DisclosureRequirement(str, Enum):
    """Disclosure requirement level."""

    NONE = "none"
    INFORM = "inform"
    CONSENT = "consent"
    EXPLICIT_CONSENT = "explicit-consent"


class HttpMethod(str, Enum):
    """HTTP methods supported by ANML actions."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class UsageRight(str, Enum):
    """Usage rights for content."""

    READ = "read"
    CACHE = "cache"
    STORE = "store"
    TRANSFORM = "transform"
    REDISTRIBUTE = "redistribute"
    TRAIN = "train"


class Confidentiality(str, Enum):
    """Confidentiality levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ParamType(str, Enum):
    """Parameter types for actions."""

    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


# --- Head models ---


class AnmlMeta(BaseModel):
    """Metadata key-value pair."""

    name: str
    content: str


class AnmlTitle(BaseModel):
    """Document title."""

    text: str = ""


class AnmlDisclosure(BaseModel):
    """Disclosure requirements for a field or operation."""

    field: str = ""
    requirement: DisclosureRequirement = DisclosureRequirement.NONE
    purpose: str = ""
    retention: str = ""


class AnmlConstraints(BaseModel):
    """Constraints on agent behavior."""

    max_requests_per_minute: int | None = Field(default=None, alias="maxRequestsPerMinute")
    max_depth: int | None = Field(default=None, alias="maxDepth")
    allowed_domains: list[str] = Field(default_factory=list, alias="allowedDomains")
    denied_domains: list[str] = Field(default_factory=list, alias="deniedDomains")

    model_config = {"populate_by_name": True}


class AnmlRights(BaseModel):
    """Usage rights for content."""

    usage: list[UsageRight] = Field(default_factory=list)
    confidentiality: Confidentiality = Confidentiality.PUBLIC
    attribution: str = ""
    license: str = ""


class AnmlHead(BaseModel):
    """Document head section."""

    title: AnmlTitle | None = None
    meta: list[AnmlMeta] = Field(default_factory=list)
    constraints: AnmlConstraints | None = None
    disclosures: list[AnmlDisclosure] = Field(default_factory=list)
    rights: AnmlRights | None = None


# --- Persona models ---


class AnmlTone(BaseModel):
    """Tone specification for persona."""

    style: str = ""
    formality: str = ""


class AnmlPersona(BaseModel):
    """Agent persona definition."""

    name: str = ""
    role: str = ""
    tone: AnmlTone | None = None


# --- Flow models ---


class AnmlContext(BaseModel):
    """Context information for a step."""

    key: str = ""
    value: str = ""
    source: str = ""


class AnmlStep(BaseModel):
    """A step in a flow."""

    id: str = ""
    label: str = ""
    status: StepStatus = StepStatus.PENDING
    context: list[AnmlContext] = Field(default_factory=list)
    next: str = ""
    conditions: list[str] = Field(default_factory=list)


class AnmlFlow(BaseModel):
    """Flow definition with ordered steps."""

    id: str = ""
    steps: list[AnmlStep] = Field(default_factory=list)


class AnmlState(BaseModel):
    """Document state section."""

    flows: list[AnmlFlow] = Field(default_factory=list)


# --- Interaction models ---


class AnmlParam(BaseModel):
    """Action parameter definition."""

    name: str = ""
    type: ParamType = ParamType.STRING
    required: bool = False
    default: Any = None
    description: str = ""
    pattern: str = ""


class AnmlAction(BaseModel):
    """An executable action."""

    id: str = ""
    method: HttpMethod = HttpMethod.GET
    url: str = ""
    params: list[AnmlParam] = Field(default_factory=list)
    headers: dict[str, str] = Field(default_factory=dict)
    body_template: str = Field(default="", alias="bodyTemplate")
    description: str = ""
    integrity: str = ""

    model_config = {"populate_by_name": True}


class AnmlInteract(BaseModel):
    """Interaction section with actions."""

    actions: list[AnmlAction] = Field(default_factory=list)


# --- Knowledge models ---


class AnmlInform(BaseModel):
    """Information provided to the agent."""

    key: str = ""
    value: str = ""
    format: str = ""
    integrity: str = ""


class AnmlAsk(BaseModel):
    """Information requested from the agent."""

    key: str = ""
    prompt: str = ""
    type: ParamType = ParamType.STRING
    required: bool = False
    options: list[str] = Field(default_factory=list)


class AnmlKnowledge(BaseModel):
    """Knowledge exchange section."""

    informs: list[AnmlInform] = Field(default_factory=list)
    asks: list[AnmlAsk] = Field(default_factory=list)


# --- Body models ---


class AnmlMedia(BaseModel):
    """Media content within the body."""

    type: str = ""
    src: str = ""
    alt: str = ""
    integrity: str = ""


class AnmlBody(BaseModel):
    """Document body content."""

    content: str = ""
    media: list[AnmlMedia] = Field(default_factory=list)


# --- Navigation models ---


class AnmlNav(BaseModel):
    """Navigation links."""

    next: str = ""
    prev: str = ""
    first: str = ""
    last: str = ""
    related: list[str] = Field(default_factory=list)


# --- Root document ---


class AnmlDocument(BaseModel):
    """Root ANML 1.0 document model."""

    version: str = "1.0"
    head: AnmlHead = Field(default_factory=AnmlHead)
    persona: AnmlPersona | None = None
    state: AnmlState | None = None
    interact: AnmlInteract | None = None
    knowledge: AnmlKnowledge | None = None
    body: AnmlBody | None = None
    nav: AnmlNav | None = None
