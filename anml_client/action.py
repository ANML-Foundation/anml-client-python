"""Action execution with parameter binding."""

from __future__ import annotations

import re
from typing import Any

import httpx

from anml_client.errors import ActionExecutionError
from anml_client.types import AnmlAction, AnmlDocument, HttpMethod


def _bind_params(template: str, params: dict[str, Any]) -> str:
    """Bind parameters into a URL or body template.

    Replaces {param_name} placeholders with parameter values.

    Args:
        template: The template string with {param} placeholders.
        params: The parameter values to bind.

    Returns:
        The template with parameters substituted.
    """

    def replacer(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in params:
            return str(params[key])
        return match.group(0)

    return re.sub(r"\{(\w+)\}", replacer, template)


def find_action(doc: AnmlDocument, action_id: str) -> AnmlAction | None:
    """Find an action by ID in a document.

    Args:
        doc: The ANML document.
        action_id: The action ID to find.

    Returns:
        The action if found, None otherwise.
    """
    if doc.interact is None:
        return None
    for action in doc.interact.actions:
        if action.id == action_id:
            return action
    return None


def build_request(
    action: AnmlAction,
    params: dict[str, Any] | None = None,
    auth_headers: dict[str, str] | None = None,
) -> httpx.Request:
    """Build an httpx Request from an ANML action.

    Args:
        action: The action to build a request for.
        params: Parameters to bind into the request.
        auth_headers: Additional authentication headers.

    Returns:
        An httpx Request object.

    Raises:
        ActionExecutionError: If the request cannot be built.
    """
    params = params or {}
    auth_headers = auth_headers or {}

    url = _bind_params(action.url, params)
    if not url:
        raise ActionExecutionError("Action has no URL")

    headers = {**action.headers, **auth_headers}

    content: str | None = None
    if action.body_template:
        content = _bind_params(action.body_template, params)

    method = action.method.value

    # Build query params for GET requests from unbound params
    query_params: dict[str, str] | None = None
    if action.method == HttpMethod.GET:
        url_param_names = set(re.findall(r"\{(\w+)\}", action.url))
        query_params = {
            k: str(v) for k, v in params.items() if k not in url_param_names
        }

    return httpx.Request(
        method=method,
        url=url,
        headers=headers,
        content=content,
        params=query_params,
    )


async def execute_action(
    http_client: httpx.AsyncClient,
    action: AnmlAction,
    params: dict[str, Any] | None = None,
    auth_headers: dict[str, str] | None = None,
) -> httpx.Response:
    """Execute an ANML action.

    Args:
        http_client: The HTTP client to use.
        action: The action to execute.
        params: Parameters to bind.
        auth_headers: Authentication headers.

    Returns:
        The HTTP response.

    Raises:
        ActionExecutionError: If execution fails.
    """
    try:
        request = build_request(action, params, auth_headers)
        response = await http_client.send(request)
        return response
    except ActionExecutionError:
        raise
    except Exception as e:
        raise ActionExecutionError(f"Failed to execute action '{action.id}': {e}") from e
