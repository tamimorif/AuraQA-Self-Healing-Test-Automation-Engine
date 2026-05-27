"""
Audit trail service for the AuraQA self-healing pipeline.

Generates ``AuditLogEntry`` records from pipeline runs for compliance,
debugging, and Jira integration.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from backend.graph.state import HealingState
from backend.models.schemas import (
    AuditLogEntry,
    DriftType,
    HealedSelectorResponse,
    HealingStatus,
    JiraPriority,
    TestFailurePayload,
)

logger = logging.getLogger(__name__)


class AuditService:
    """
    Constructs and persists audit log entries.

    In a production deployment this would write to a database or external
    audit log service.  Currently it builds the ``AuditLogEntry`` model
    in-memory and logs it.
    """

    def __init__(self) -> None:
        # In-memory store for dev/test — swap for a DB in production
        self._entries: list[AuditLogEntry] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_entry(
        self,
        payload: TestFailurePayload,
        state: HealingState,
        response: HealedSelectorResponse,
    ) -> AuditLogEntry:
        """
        Build an audit log entry from the pipeline inputs and outputs.

        Args:
            payload:  Original test-failure payload.
            state:    Final LangGraph state after pipeline execution.
            response: The ``HealedSelectorResponse`` being returned to UiPath.

        Returns:
            A fully populated ``AuditLogEntry``.
        """
        candidates = state.get("candidate_selectors", [])
        top_breakdown = candidates[0].get("breakdown", {}) if candidates else {}

        drift_type = _safe_drift(state.get("drift_type", ""))
        priority = _determine_priority(response.confidence)

        # Pull Jira key from escalation audit if present
        audit_log_raw = state.get("audit_log", {})
        jira_key = audit_log_raw.get("jira_issue_key")

        entry = AuditLogEntry(
            audit_id=str(uuid.uuid4()),
            test_case_id=payload.test_case_id,
            test_suite_id=payload.test_suite_id,
            original_selector=payload.broken_selector,
            healed_selector=response.healed_selector if response.status == HealingStatus.HEALED else None,
            confidence=response.confidence,
            status=response.status,
            drift_type=drift_type,
            attempt_count=response.attempt_count,
            execution_time_ms=response.execution_time_ms,
            page_url=payload.page_url,
            environment=payload.environment,
            error_message=state.get("error_message", ""),
            scoring_breakdown=top_breakdown,
            jira_issue_key=jira_key,
            jira_priority=priority,
        )

        self._entries.append(entry)
        logger.info(
            "AuditService — created entry %s for %s (status=%s)",
            entry.audit_id,
            entry.test_case_id,
            entry.status.value,
        )
        return entry

    def get_entries(self) -> list[AuditLogEntry]:
        """Return all stored audit log entries (most-recent first)."""
        return list(reversed(self._entries))

    def get_entry(self, audit_id: str) -> AuditLogEntry | None:
        """Look up a single audit entry by ID."""
        for entry in self._entries:
            if entry.audit_id == audit_id:
                return entry
        return None


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _safe_drift(raw: str) -> DriftType | None:
    if not raw:
        return None
    try:
        return DriftType(raw)
    except ValueError:
        return None


def _determine_priority(confidence: float) -> JiraPriority:
    if confidence < 20.0:
        return JiraPriority.CRITICAL
    if confidence < 50.0:
        return JiraPriority.HIGH
    if confidence < 80.0:
        return JiraPriority.MEDIUM
    return JiraPriority.LOW
