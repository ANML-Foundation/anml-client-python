"""Flow navigation utilities."""

from __future__ import annotations

from anml_client.types import AnmlDocument, AnmlFlow, AnmlStep, StepStatus


def get_current_step(doc: AnmlDocument) -> AnmlStep | None:
    """Get the currently active step in the first flow.

    Args:
        doc: The ANML document.

    Returns:
        The active step, or None if no step is active.
    """
    if doc.state is None or not doc.state.flows:
        return None

    flow = doc.state.flows[0]
    for step in flow.steps:
        if step.status == StepStatus.ACTIVE:
            return step
    return None


def get_next_step(doc: AnmlDocument) -> AnmlStep | None:
    """Get the next pending step after the current active step.

    Args:
        doc: The ANML document.

    Returns:
        The next pending step, or None if no next step exists.
    """
    if doc.state is None or not doc.state.flows:
        return None

    flow = doc.state.flows[0]
    found_active = False
    for step in flow.steps:
        if step.status == StepStatus.ACTIVE:
            found_active = True
            continue
        if found_active and step.status == StepStatus.PENDING:
            return step

    # If no active step found, return first pending
    if not found_active:
        for step in flow.steps:
            if step.status == StepStatus.PENDING:
                return step

    return None


def is_flow_complete(doc: AnmlDocument) -> bool:
    """Check if all steps in the first flow are complete or skipped.

    Args:
        doc: The ANML document.

    Returns:
        True if the flow is complete.
    """
    if doc.state is None or not doc.state.flows:
        return True

    flow = doc.state.flows[0]
    if not flow.steps:
        return True

    return all(
        step.status in (StepStatus.COMPLETE, StepStatus.SKIPPED) for step in flow.steps
    )


class FlowNavigator:
    """Utility class for navigating flows in an ANML document."""

    def __init__(self, doc: AnmlDocument) -> None:
        self._doc = doc

    @property
    def flows(self) -> list[AnmlFlow]:
        """Get all flows in the document."""
        if self._doc.state is None:
            return []
        return self._doc.state.flows

    @property
    def current_step(self) -> AnmlStep | None:
        """Get the current active step."""
        return get_current_step(self._doc)

    @property
    def next_step(self) -> AnmlStep | None:
        """Get the next pending step."""
        return get_next_step(self._doc)

    @property
    def is_complete(self) -> bool:
        """Check if the flow is complete."""
        return is_flow_complete(self._doc)

    def get_step_by_id(self, step_id: str) -> AnmlStep | None:
        """Find a step by its ID across all flows.

        Args:
            step_id: The step ID to find.

        Returns:
            The step if found, None otherwise.
        """
        for flow in self.flows:
            for step in flow.steps:
                if step.id == step_id:
                    return step
        return None

    def get_completed_steps(self) -> list[AnmlStep]:
        """Get all completed steps across all flows."""
        completed = []
        for flow in self.flows:
            for step in flow.steps:
                if step.status == StepStatus.COMPLETE:
                    completed.append(step)
        return completed

    def get_pending_steps(self) -> list[AnmlStep]:
        """Get all pending steps across all flows."""
        pending = []
        for flow in self.flows:
            for step in flow.steps:
                if step.status == StepStatus.PENDING:
                    pending.append(step)
        return pending
