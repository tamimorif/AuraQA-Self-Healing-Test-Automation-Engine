"""
LangGraph conditional-edge routing logic.

Determines the next node after selector validation:
    - confidence ≥ threshold  →  rerun_test
    - attempts < max_retries  →  generate_selector  (retry)
    - else                    →  escalate
"""
from __future__ import annotations

import logging

from backend.config.settings import get_settings
from backend.graph.state import HealingState
from backend.models.schemas import HealingStatus

logger = logging.getLogger(__name__)


def route_after_validation(state: HealingState) -> str:
    """
    Conditional edge function invoked after ``validate_selector``.

    Returns:
        The name of the next LangGraph node to execute:
        ``"rerun_test"``, ``"generate_selector"``, or ``"escalate"``.
    """
    status = state.get("status", "")
    confidence = state.get("confidence_score", 0.0)
    attempt_count = state.get("attempt_count", 1)
    max_retries = state.get("max_retries", 3)
    settings = get_settings()
    threshold = settings.confidence_threshold

    logger.info(
        "route_after_validation — status=%s confidence=%.2f attempt=%d/%d threshold=%.2f",
        status,
        confidence,
        attempt_count,
        max_retries,
        threshold,
    )

    # 1. Healed successfully
    if status == HealingStatus.HEALED.value and confidence >= threshold:
        logger.info("route → rerun_test (healed)")
        return "rerun_test"

    # 2. Can still retry
    if attempt_count < max_retries:
        state["attempt_count"] = attempt_count + 1
        state["status"] = HealingStatus.RETRYING.value
        logger.info("route → generate_selector (retry %d)", state["attempt_count"])
        return "generate_selector"

    # 3. Exhausted retries — escalate
    logger.info("route → escalate (max retries exhausted)")
    return "escalate"
