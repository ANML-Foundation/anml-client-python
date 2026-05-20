"""Knowledge exchange helpers."""

from __future__ import annotations

from anml_client.types import AnmlAsk, AnmlDocument, AnmlInform


def get_informs(doc: AnmlDocument) -> list[AnmlInform]:
    """Get all inform elements from a document.

    Args:
        doc: The ANML document.

    Returns:
        List of inform elements.
    """
    if doc.knowledge is None:
        return []
    return doc.knowledge.informs


def get_asks(doc: AnmlDocument) -> list[AnmlAsk]:
    """Get all ask elements from a document.

    Args:
        doc: The ANML document.

    Returns:
        List of ask elements.
    """
    if doc.knowledge is None:
        return []
    return doc.knowledge.asks


def get_inform_by_key(doc: AnmlDocument, key: str) -> AnmlInform | None:
    """Find an inform element by key.

    Args:
        doc: The ANML document.
        key: The key to search for.

    Returns:
        The inform element if found, None otherwise.
    """
    for inform in get_informs(doc):
        if inform.key == key:
            return inform
    return None


def get_ask_by_key(doc: AnmlDocument, key: str) -> AnmlAsk | None:
    """Find an ask element by key.

    Args:
        doc: The ANML document.
        key: The key to search for.

    Returns:
        The ask element if found, None otherwise.
    """
    for ask in get_asks(doc):
        if ask.key == key:
            return ask
    return None


def get_required_asks(doc: AnmlDocument) -> list[AnmlAsk]:
    """Get all required ask elements.

    Args:
        doc: The ANML document.

    Returns:
        List of required ask elements.
    """
    return [ask for ask in get_asks(doc) if ask.required]
