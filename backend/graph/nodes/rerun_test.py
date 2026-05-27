"""
LangGraph node: trigger test re-execution with the healed selector.

In a production environment this node would call the UiPath Orchestrator
API to re-queue the test.  For now it records the intent and marks the
pipeline as HEALED.
"""
from __future__ import annotations

import logging
import time

from backend.graph.state import HealingState
from backend.models.schemas import HealingStatus

logger = logging.getLogger(__name__)


def rerun_test(state: HealingState) -> HealingState:
    """
    Record the healed selector and finalise the pipeline.

    In a full integration this would POST to UiPath Orchestrator.
    Here we capture timing, finalise the audit log seed, and confirm
    the HEALED status.

    Updates:
        - ``status`` → HEALED
        - ``audit_log`` — populated with summary data
    """
    logger.info("rerun_test — finalising healed pipeline run")

    state["status"] = HealingStatus.HEALED.value

    execution_start = state.get("execution_start_ms", 0.0)
    execution_time_ms = (time.time() * 1000) - execution_start if execution_start else 0.0

    failure = state.get("failure_payload", {})
    candidates = state.get("candidate_selectors", [])
    top_breakdown = candidates[0].get("breakdown", {}) if candidates else {}

    state["audit_log"] = {
        "test_case_id": failure.get("test_case_id", ""),
        "test_suite_id": failure.get("test_suite_id", ""),
        "original_selector": failure.get("broken_selector", ""),
        "healed_selector": state.get("healed_selector", ""),
        "confidence": state.get("confidence_score", 0.0),
        "status": HealingStatus.HEALED.value,
        "drift_type": state.get("drift_type", ""),
        "attempt_count": state.get("attempt_count", 1),
        "execution_time_ms": round(execution_time_ms, 2),
        "page_url": failure.get("page_url", ""),
        "environment": failure.get("environment", "staging"),
        "scoring_breakdown": top_breakdown,
    }

    logger.info(
        "rerun_test — healed selector=%s confidence=%.2f in %.0f ms",
        state.get("healed_selector", ""),
        state.get("confidence_score", 0.0),
        execution_time_ms,
    )
    return state
