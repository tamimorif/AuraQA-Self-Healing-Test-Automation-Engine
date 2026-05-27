"""
LangGraph node: escalate to Jira when healing fails.

Creates a Jira issue through the JiraClient and marks the pipeline as
ESCALATED so UiPath knows the failure requires human attention.
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid

from backend.graph.state import HealingState
from backend.graph.tools.jira_client import JiraClient
from backend.models.schemas import (
    AuditLogEntry,
    DriftType,
    HealingStatus,
    JiraPriority,
)

logger = logging.getLogger(__name__)


def escalate(state: HealingState) -> HealingState:
    """
    Escalate the failure to Jira.

    Updates:
        - ``status``     → ESCALATED
        - ``audit_log``  — enriched with Jira issue key
    """
    logger.info("escalate — creating Jira issue for unhealed failure")

    state["status"] = HealingStatus.ESCALATED.value

    failure = state.get("failure_payload", {})
    candidates = state.get("candidate_selectors", [])
    top_breakdown = candidates[0].get("breakdown", {}) if candidates else {}

    execution_start = state.get("execution_start_ms", 0.0)
    execution_time_ms = (time.time() * 1000) - execution_start if execution_start else 0.0

    drift_raw = state.get("drift_type", "")
    drift_type = _parse_drift(drift_raw)

    # Determine priority based on confidence
    confidence = state.get("confidence_score", 0.0)
    priority = _determine_priority(confidence)

    audit = AuditLogEntry(
        audit_id=str(uuid.uuid4()),
        test_case_id=failure.get("test_case_id", "unknown"),
        test_suite_id=failure.get("test_suite_id", "unknown"),
        original_selector=failure.get("broken_selector", ""),
        healed_selector=state.get("healed_selector") or None,
        confidence=confidence,
        status=HealingStatus.ESCALATED,
        drift_type=drift_type,
        attempt_count=state.get("attempt_count", 1),
        execution_time_ms=round(execution_time_ms, 2),
        page_url=failure.get("page_url", ""),
        environment=failure.get("environment", "staging"),
        error_message=state.get("error_message", ""),
        scoring_breakdown=top_breakdown,
        jira_priority=priority,
    )

    # Create Jira issue (async bridged to sync)
    jira_key = _create_jira_issue(audit, priority)
    audit.jira_issue_key = jira_key

    state["audit_log"] = audit.model_dump(mode="json")
    logger.info("escalate — Jira issue %s created (priority=%s)", jira_key, priority.value)
    return state


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _create_jira_issue(audit: AuditLogEntry, priority: JiraPriority) -> str:
    """Bridge async JiraClient into the sync LangGraph node."""
    client = JiraClient()
    try:
        loop = _get_or_create_event_loop()
        return loop.run_until_complete(client.create_issue(audit, priority=priority))
    except Exception as exc:
        logger.error("escalate — Jira creation failed: %s", exc)
        return f"JIRA-ERROR-{uuid.uuid4().hex[:8]}"


def _determine_priority(confidence: float) -> JiraPriority:
    """Map confidence to Jira priority."""
    if confidence < 20.0:
        return JiraPriority.CRITICAL
    if confidence < 50.0:
        return JiraPriority.HIGH
    if confidence < 80.0:
        return JiraPriority.MEDIUM
    return JiraPriority.LOW


def _parse_drift(raw: str) -> DriftType | None:
    """Safely parse a drift type string."""
    if not raw:
        return None
    try:
        return DriftType(raw)
    except ValueError:
        return None


def _get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("closed")
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
