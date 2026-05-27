"""
LangGraph healing-pipeline state definition and factory.

Re-exports ``HealingState`` from the canonical schemas module and
provides ``create_initial_state()`` for ergonomic pipeline bootstrapping.
"""
from __future__ import annotations

import time
from typing import Any

from backend.models.schemas import (
    HealingState,
    HealingStatus,
    TestFailurePayload,
)


# Re-export so downstream modules can do:
#   from backend.graph.state import HealingState, create_initial_state
__all__ = ["HealingState", "create_initial_state"]


def create_initial_state(
    payload: TestFailurePayload,
    *,
    max_retries: int = 3,
) -> HealingState:
    """
    Build the initial ``HealingState`` dict from a test-failure payload.

    Args:
        payload: Validated test-failure data received from UiPath.
        max_retries: Maximum number of healing attempts before escalation.

    Returns:
        A ``HealingState`` dict ready to be fed into the LangGraph pipeline.
    """
    return HealingState(
        failure_payload=payload.model_dump(mode="json"),
        dom_snapshot=payload.dom_snapshot,
        parsed_elements=[],
        original_attributes=payload.original_element_attributes.model_dump(mode="json"),
        candidate_selectors=[],
        healed_selector="",
        healed_selector_type="",
        confidence_score=0.0,
        drift_type="",
        attempt_count=payload.retry_count + 1,
        max_retries=max_retries,
        status=HealingStatus.PENDING.value,
        audit_log={},
        tdo_data={},
        error_message="",
        execution_start_ms=time.time() * 1000,
    )
