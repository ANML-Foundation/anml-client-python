"""XML and JSON parsing for ANML 1.0 documents."""

from __future__ import annotations

import json
from typing import Any
from xml.etree.ElementTree import Element

import defusedxml.ElementTree as ET

from anml_client.errors import ParseError
from anml_client.types import (
    AnmlAction,
    AnmlAsk,
    AnmlBody,
    AnmlConstraints,
    AnmlContext,
    AnmlDisclosure,
    AnmlDocument,
    AnmlFlow,
    AnmlHead,
    AnmlInform,
    AnmlInteract,
    AnmlKnowledge,
    AnmlMedia,
    AnmlMeta,
    AnmlNav,
    AnmlParam,
    AnmlPersona,
    AnmlRights,
    AnmlState,
    AnmlStep,
    AnmlTitle,
    AnmlTone,
    Confidentiality,
    DisclosureRequirement,
    HttpMethod,
    ParamType,
    StepStatus,
    UsageRight,
)


def _get_text(element: Element, tag: str, default: str = "") -> str:
    """Get text content of a child element."""
    child = element.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return default


def _get_attr(element: Element, attr: str, default: str = "") -> str:
    """Get attribute value with default."""
    return element.get(attr, default)


def _parse_meta(element: Element) -> list[AnmlMeta]:
    """Parse meta elements."""
    metas = []
    for meta_el in element.findall("meta"):
        metas.append(
            AnmlMeta(
                name=_get_attr(meta_el, "name"),
                content=_get_attr(meta_el, "content"),
            )
        )
    return metas


def _parse_disclosures(element: Element) -> list[AnmlDisclosure]:
    """Parse disclosure elements."""
    disclosures = []
    for disc_el in element.findall("disclosure"):
        req_str = _get_attr(disc_el, "requirement", "none")
        try:
            requirement = DisclosureRequirement(req_str)
        except ValueError:
            requirement = DisclosureRequirement.NONE
        disclosures.append(
            AnmlDisclosure(
                field=_get_attr(disc_el, "field"),
                requirement=requirement,
                purpose=_get_attr(disc_el, "purpose"),
                retention=_get_attr(disc_el, "retention"),
            )
        )
    return disclosures


def _parse_constraints(element: Element) -> AnmlConstraints | None:
    """Parse constraints element."""
    constraints_el = element.find("constraints")
    if constraints_el is None:
        return None

    allowed = []
    for domain_el in constraints_el.findall("allowed-domain"):
        if domain_el.text:
            allowed.append(domain_el.text.strip())

    denied = []
    for domain_el in constraints_el.findall("denied-domain"):
        if domain_el.text:
            denied.append(domain_el.text.strip())

    max_rpm_str = _get_attr(constraints_el, "max-requests-per-minute")
    max_depth_str = _get_attr(constraints_el, "max-depth")

    return AnmlConstraints(
        maxRequestsPerMinute=int(max_rpm_str) if max_rpm_str else None,
        maxDepth=int(max_depth_str) if max_depth_str else None,
        allowedDomains=allowed,
        deniedDomains=denied,
    )


def _parse_rights(element: Element) -> AnmlRights | None:
    """Parse rights element."""
    rights_el = element.find("rights")
    if rights_el is None:
        return None

    usage_strs = _get_attr(rights_el, "usage").split(",") if _get_attr(rights_el, "usage") else []
    usage = []
    for u in usage_strs:
        u = u.strip()
        if u:
            try:
                usage.append(UsageRight(u))
            except ValueError:
                pass

    conf_str = _get_attr(rights_el, "confidentiality", "public")
    try:
        confidentiality = Confidentiality(conf_str)
    except ValueError:
        confidentiality = Confidentiality.PUBLIC

    return AnmlRights(
        usage=usage,
        confidentiality=confidentiality,
        attribution=_get_attr(rights_el, "attribution"),
        license=_get_attr(rights_el, "license"),
    )


def _parse_head(element: Element) -> AnmlHead:
    """Parse head element."""
    head_el = element.find("head")
    if head_el is None:
        return AnmlHead()

    title_el = head_el.find("title")
    title = AnmlTitle(text=title_el.text.strip() if title_el is not None and title_el.text else "")

    return AnmlHead(
        title=title,
        meta=_parse_meta(head_el),
        constraints=_parse_constraints(head_el),
        disclosures=_parse_disclosures(head_el),
        rights=_parse_rights(head_el),
    )


def _parse_persona(element: Element) -> AnmlPersona | None:
    """Parse persona element."""
    persona_el = element.find("persona")
    if persona_el is None:
        return None

    tone_el = persona_el.find("tone")
    tone = None
    if tone_el is not None:
        tone = AnmlTone(
            style=_get_attr(tone_el, "style"),
            formality=_get_attr(tone_el, "formality"),
        )

    return AnmlPersona(
        name=_get_attr(persona_el, "name"),
        role=_get_attr(persona_el, "role"),
        tone=tone,
    )


def _parse_steps(flow_el: Element) -> list[AnmlStep]:
    """Parse step elements within a flow."""
    steps = []
    for step_el in flow_el.findall("step"):
        status_str = _get_attr(step_el, "status", "pending")
        try:
            status = StepStatus(status_str)
        except ValueError:
            status = StepStatus.PENDING

        contexts = []
        for ctx_el in step_el.findall("context"):
            contexts.append(
                AnmlContext(
                    key=_get_attr(ctx_el, "key"),
                    value=_get_attr(ctx_el, "value"),
                    source=_get_attr(ctx_el, "source"),
                )
            )

        conditions = []
        for cond_el in step_el.findall("condition"):
            if cond_el.text:
                conditions.append(cond_el.text.strip())

        steps.append(
            AnmlStep(
                id=_get_attr(step_el, "id"),
                label=_get_attr(step_el, "label"),
                status=status,
                context=contexts,
                next=_get_attr(step_el, "next"),
                conditions=conditions,
            )
        )
    return steps


def _parse_state(element: Element) -> AnmlState | None:
    """Parse state element."""
    state_el = element.find("state")
    if state_el is None:
        return None

    flows = []
    for flow_el in state_el.findall("flow"):
        flows.append(
            AnmlFlow(
                id=_get_attr(flow_el, "id"),
                steps=_parse_steps(flow_el),
            )
        )

    return AnmlState(flows=flows)


def _parse_params(action_el: Element) -> list[AnmlParam]:
    """Parse param elements within an action."""
    params = []
    for param_el in action_el.findall("param"):
        type_str = _get_attr(param_el, "type", "string")
        try:
            param_type = ParamType(type_str)
        except ValueError:
            param_type = ParamType.STRING

        required_str = _get_attr(param_el, "required", "false")

        params.append(
            AnmlParam(
                name=_get_attr(param_el, "name"),
                type=param_type,
                required=required_str.lower() in ("true", "1", "yes"),
                default=_get_attr(param_el, "default") or None,
                description=_get_attr(param_el, "description"),
                pattern=_get_attr(param_el, "pattern"),
            )
        )
    return params


def _parse_interact(element: Element) -> AnmlInteract | None:
    """Parse interact element."""
    interact_el = element.find("interact")
    if interact_el is None:
        return None

    actions = []
    for action_el in interact_el.findall("action"):
        method_str = _get_attr(action_el, "method", "GET").upper()
        try:
            method = HttpMethod(method_str)
        except ValueError:
            method = HttpMethod.GET

        headers: dict[str, str] = {}
        for header_el in action_el.findall("header"):
            name = _get_attr(header_el, "name")
            value = _get_attr(header_el, "value")
            if name:
                headers[name] = value

        actions.append(
            AnmlAction(
                id=_get_attr(action_el, "id"),
                method=method,
                url=_get_attr(action_el, "url"),
                params=_parse_params(action_el),
                headers=headers,
                bodyTemplate=_get_text(action_el, "body-template"),
                description=_get_attr(action_el, "description"),
                integrity=_get_attr(action_el, "integrity"),
            )
        )

    return AnmlInteract(actions=actions)


def _parse_knowledge(element: Element) -> AnmlKnowledge | None:
    """Parse knowledge element."""
    knowledge_el = element.find("knowledge")
    if knowledge_el is None:
        return None

    informs = []
    for inform_el in knowledge_el.findall("inform"):
        informs.append(
            AnmlInform(
                key=_get_attr(inform_el, "key"),
                value=inform_el.text.strip() if inform_el.text else _get_attr(inform_el, "value"),
                format=_get_attr(inform_el, "format"),
                integrity=_get_attr(inform_el, "integrity"),
            )
        )

    asks = []
    for ask_el in knowledge_el.findall("ask"):
        type_str = _get_attr(ask_el, "type", "string")
        try:
            ask_type = ParamType(type_str)
        except ValueError:
            ask_type = ParamType.STRING

        options = []
        for opt_el in ask_el.findall("option"):
            if opt_el.text:
                options.append(opt_el.text.strip())

        asks.append(
            AnmlAsk(
                key=_get_attr(ask_el, "key"),
                prompt=_get_attr(ask_el, "prompt"),
                type=ask_type,
                required=_get_attr(ask_el, "required", "false").lower() in ("true", "1", "yes"),
                options=options,
            )
        )

    return AnmlKnowledge(informs=informs, asks=asks)


def _parse_body(element: Element) -> AnmlBody | None:
    """Parse body element."""
    body_el = element.find("body")
    if body_el is None:
        return None

    content = ""
    content_el = body_el.find("content")
    if content_el is not None and content_el.text:
        content = content_el.text.strip()
    elif body_el.text:
        content = body_el.text.strip()

    media_list = []
    for media_el in body_el.findall("media"):
        media_list.append(
            AnmlMedia(
                type=_get_attr(media_el, "type"),
                src=_get_attr(media_el, "src"),
                alt=_get_attr(media_el, "alt"),
                integrity=_get_attr(media_el, "integrity"),
            )
        )

    return AnmlBody(content=content, media=media_list)


def _parse_nav(element: Element) -> AnmlNav | None:
    """Parse nav element."""
    nav_el = element.find("nav")
    if nav_el is None:
        return None

    related = []
    for rel_el in nav_el.findall("related"):
        href = _get_attr(rel_el, "href")
        if href:
            related.append(href)

    return AnmlNav(
        next=_get_attr(nav_el, "next"),
        prev=_get_attr(nav_el, "prev"),
        first=_get_attr(nav_el, "first"),
        last=_get_attr(nav_el, "last"),
        related=related,
    )


def parse_anml_xml(xml: str) -> AnmlDocument:
    """Parse an ANML XML document string into an AnmlDocument model.

    Args:
        xml: The XML string to parse.

    Returns:
        Parsed AnmlDocument.

    Raises:
        ParseError: If the XML cannot be parsed.
    """
    try:
        root = ET.fromstring(xml)
    except Exception as e:
        raise ParseError(f"Failed to parse ANML XML: {e}") from e

    version = _get_attr(root, "version", "1.0")

    return AnmlDocument(
        version=version,
        head=_parse_head(root),
        persona=_parse_persona(root),
        state=_parse_state(root),
        interact=_parse_interact(root),
        knowledge=_parse_knowledge(root),
        body=_parse_body(root),
        nav=_parse_nav(root),
    )


def _build_document_from_dict(data: dict[str, Any]) -> AnmlDocument:
    """Build an AnmlDocument from a dictionary (JSON-parsed data)."""
    return AnmlDocument.model_validate(data)


def parse_anml_json(json_str: str) -> AnmlDocument:
    """Parse an ANML JSON document string into an AnmlDocument model.

    Args:
        json_str: The JSON string to parse.

    Returns:
        Parsed AnmlDocument.

    Raises:
        ParseError: If the JSON cannot be parsed.
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ParseError(f"Failed to parse ANML JSON: {e}") from e

    try:
        return _build_document_from_dict(data)
    except Exception as e:
        raise ParseError(f"Failed to validate ANML document: {e}") from e


def parse_anml(content: str, content_type: str) -> AnmlDocument:
    """Parse an ANML document based on content type.

    Args:
        content: The document content string.
        content_type: MIME type (e.g., 'application/anml+xml', 'application/anml+json').

    Returns:
        Parsed AnmlDocument.

    Raises:
        ParseError: If the content type is unsupported or parsing fails.
    """
    ct = content_type.lower().split(";")[0].strip()

    if "xml" in ct or ct == "text/xml":
        return parse_anml_xml(content)
    elif "json" in ct:
        return parse_anml_json(content)
    else:
        # Try XML first, then JSON
        try:
            return parse_anml_xml(content)
        except ParseError:
            try:
                return parse_anml_json(content)
            except ParseError:
                raise ParseError(
                    f"Unable to parse ANML document with content type: {content_type}"
                )
