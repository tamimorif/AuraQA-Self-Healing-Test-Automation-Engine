"""
Healing service — orchestrates the full self-healing pipeline.

Entry point for the FastAPI endpoint.  Accepts a ``TestFailurePayload``,
runs it through the compiled LangGraph, and returns a
``HealedSelectorResponse``.
"""
from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from backend.config.settings import get_settings
from backend.graph.graph import build_healing_graph
from backend.graph.state import HealingState, create_initial_state
from backend.models.schemas import (
    CandidateSelector,
    DOMElement,
    DriftType,
    HealedSelectorResponse,
    HealingStatus,
    SelectorType,
    TestFailurePayload,
)
from backend.services.audit_service import AuditService

logger = logging.getLogger(__name__)

# Module-level compiled graph — built once, reused.
_compiled_graph = None


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_healing_graph()
    return _compiled_graph


class HealingService:
    """
    Orchestrates the self-healing pipeline end-to-end.

    Usage::

        service = HealingService()
        response = await service.heal(payload)
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.audit_service = AuditService()

    async def heal(self, payload: TestFailurePayload) -> HealedSelectorResponse:
        """
        Run the full healing pipeline.

        Args:
            payload: Validated test-failure data from UiPath.

        Returns:
            ``HealedSelectorResponse`` with the healed selector or
            escalation metadata.
        """
        start_ms = time.time() * 1000
        logger.info(
            "HealingService.heal — test_case=%s selector=%s",
            payload.test_case_id,
            payload.broken_selector,
        )

        # 1. Build initial state
        initial_state = create_initial_state(
            payload,
            max_retries=self.settings.langgraph_max_retries,
        )

        # 2. Run LangGraph
        graph = _get_graph()
        final_state: HealingState = graph.invoke(initial_state)

        # 3. Build response
        execution_time_ms = (time.time() * 1000) - start_ms
        response = self._build_response(payload, final_state, execution_time_ms)

        # 4. Create audit trail
        audit_entry = self.audit_service.create_entry(payload, final_state, response)
        response.audit_log_id = audit_entry.audit_id

        logger.info(
            "HealingService.heal — status=%s confidence=%.2f time=%.0f ms",
            response.status.value,
            response.confidence,
            execution_time_ms,
        )
        return response

    # ------------------------------------------------------------------
    # Response construction
    # ------------------------------------------------------------------

    def _build_response(
        self,
        payload: TestFailurePayload,
        state: HealingState,
        execution_time_ms: float,
    ) -> HealedSelectorResponse:
        """Build the API response from final pipeline state."""
        status_str = state.get("status", HealingStatus.FAILED.value)
        try:
            status = HealingStatus(status_str)
        except ValueError:
            status = HealingStatus.FAILED

        healed_selector = state.get("healed_selector", "")
        healed_type_str = state.get("healed_selector_type", SelectorType.CSS.value)
        try:
            healed_type = SelectorType(healed_type_str)
        except ValueError:
            healed_type = SelectorType.CSS

        confidence = state.get("confidence_score", 0.0)

        drift_raw = state.get("drift_type", "")
        drift_type = _safe_drift(drift_raw)

        candidates_raw = state.get("candidate_selectors", [])
        top_candidates = self._build_candidates(candidates_raw)

        return HealedSelectorResponse(
            test_case_id=payload.test_case_id,
            original_selector=payload.broken_selector,
            healed_selector=healed_selector or payload.broken_selector,
            healed_selector_type=healed_type,
            confidence=confidence,
            status=status,
            candidates_evaluated=len(state.get("parsed_elements", [])),
            top_candidates=top_candidates,
            drift_type=drift_type,
            attempt_count=state.get("attempt_count", 1),
            execution_time_ms=round(execution_time_ms, 2),
            audit_log_id=None,
        )

    @staticmethod
    def _build_candidates(raw: list[dict[str, Any]]) -> list[CandidateSelector]:
        """Convert raw state dicts into ``CandidateSelector`` models."""
        result: list[CandidateSelector] = []
        for entry in raw[:3]:
            elem_data = entry.get("element", {})
            composite = entry.get("composite_score", 0.0)
            breakdown = entry.get("breakdown", {})

            try:
                elem = DOMElement(**elem_data)
            except Exception:
                elem = None

            # Determine selector type from element properties
            if elem and elem.data_testid:
                sel = f'[data-testid="{elem.data_testid}"]'
                sel_type = SelectorType.DATA_TESTID
            elif elem and elem.element_id:
                sel = f"#{elem.element_id}"
                sel_type = SelectorType.CSS
            elif elem and elem.classes:
                sel = f"{elem.tag}.{'.'.join(elem.classes)}"
                sel_type = SelectorType.CSS
            elif elem and elem.xpath:
                sel = elem.xpath
                sel_type = SelectorType.XPATH
            else:
                sel = "unknown"
                sel_type = SelectorType.CSS

            result.append(
                CandidateSelector(
                    selector=sel,
                    selector_type=sel_type,
                    confidence=composite,
                    matched_element=elem,
                    scoring_breakdown=breakdown,
                )
            )
        return result


def _safe_drift(raw: str) -> DriftType | None:
    if not raw:
        return None
    try:
        return DriftType(raw)
    except ValueError:
        return None
