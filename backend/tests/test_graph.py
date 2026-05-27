"""
Integration tests for the LangGraph healing pipeline and FastAPI endpoint.
"""
from __future__ import annotations

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.graph.graph import build_healing_graph
from backend.graph.state import HealingState, create_initial_state
from backend.models.schemas import (
    HealedSelectorResponse,
    HealingStatus,
    SelectorType,
    TestFailurePayload,
)


# ------------------------------------------------------------------
# State factory
# ------------------------------------------------------------------

class TestCreateInitialState:
    """Tests for create_initial_state()."""

    def test_creates_valid_state(self, test_failure_payload: TestFailurePayload) -> None:
        state = create_initial_state(test_failure_payload)
        assert state["status"] == HealingStatus.PENDING.value
        assert state["dom_snapshot"] == test_failure_payload.dom_snapshot
        assert state["attempt_count"] == 1
        assert state["max_retries"] == 3
        assert state["healed_selector"] == ""
        assert state["execution_start_ms"] > 0

    def test_respects_max_retries(self, test_failure_payload: TestFailurePayload) -> None:
        state = create_initial_state(test_failure_payload, max_retries=5)
        assert state["max_retries"] == 5

    def test_preserves_retry_count(self, test_failure_payload: TestFailurePayload) -> None:
        test_failure_payload.retry_count = 2
        state = create_initial_state(test_failure_payload)
        assert state["attempt_count"] == 3  # retry_count + 1


# ------------------------------------------------------------------
# Full pipeline — healed path
# ------------------------------------------------------------------

class TestHealingGraphIntegration:
    """End-to-end LangGraph pipeline tests."""

    def test_heals_exact_match(self, test_failure_payload: TestFailurePayload) -> None:
        """Pipeline should heal when the original element is still in the DOM."""
        state = create_initial_state(test_failure_payload)
        graph = build_healing_graph()
        result = graph.invoke(state)

        assert result["status"] in (
            HealingStatus.HEALED.value,
            HealingStatus.ESCALATED.value,
        )
        assert result["healed_selector"] != ""
        assert result["confidence_score"] > 0

    def test_heals_with_high_confidence(self, test_failure_payload: TestFailurePayload) -> None:
        """When the exact element exists, confidence should be ≥ 80%."""
        state = create_initial_state(test_failure_payload)
        graph = build_healing_graph()
        result = graph.invoke(state)

        if result["status"] == HealingStatus.HEALED.value:
            assert result["confidence_score"] >= 80.0

    def test_generates_candidates(self, test_failure_payload: TestFailurePayload) -> None:
        """Pipeline should produce candidate selectors."""
        state = create_initial_state(test_failure_payload)
        graph = build_healing_graph()
        result = graph.invoke(state)

        candidates = result.get("candidate_selectors", [])
        assert len(candidates) > 0

    def test_populates_audit_log(self, test_failure_payload: TestFailurePayload) -> None:
        """Pipeline should populate the audit log."""
        state = create_initial_state(test_failure_payload)
        graph = build_healing_graph()
        result = graph.invoke(state)

        audit = result.get("audit_log", {})
        assert audit.get("test_case_id") == "TC-001"

    def test_drifted_dom_still_heals_or_escalates(
        self,
        drifted_failure_payload: TestFailurePayload,
    ) -> None:
        """Even with a drifted DOM, the pipeline should complete."""
        state = create_initial_state(drifted_failure_payload)
        graph = build_healing_graph()
        result = graph.invoke(state)

        assert result["status"] in (
            HealingStatus.HEALED.value,
            HealingStatus.ESCALATED.value,
        )

    def test_parsed_elements_populated(self, test_failure_payload: TestFailurePayload) -> None:
        state = create_initial_state(test_failure_payload)
        graph = build_healing_graph()
        result = graph.invoke(state)

        parsed = result.get("parsed_elements", [])
        assert len(parsed) > 0


# ------------------------------------------------------------------
# Individual node tests (via direct import)
# ------------------------------------------------------------------

class TestAnalyzeDomNode:
    """Tests for the analyze_dom node in isolation."""

    def test_parses_elements(self, test_failure_payload: TestFailurePayload) -> None:
        from backend.graph.nodes.analyze_dom import analyze_dom

        state = create_initial_state(test_failure_payload)
        result = analyze_dom(state)

        assert len(result["parsed_elements"]) > 0
        assert len(result["candidate_selectors"]) > 0
        assert result["status"] == HealingStatus.ANALYZING.value

    def test_handles_empty_dom(self) -> None:
        from backend.graph.nodes.analyze_dom import analyze_dom
        from backend.models.schemas import OriginalElementAttributes

        state: HealingState = {
            "dom_snapshot": "<html><body></body></html>",
            "original_attributes": OriginalElementAttributes(tag="div").model_dump(mode="json"),
            "parsed_elements": [],
            "candidate_selectors": [],
            "status": HealingStatus.PENDING.value,
            "failure_payload": {},
            "healed_selector": "",
            "healed_selector_type": "",
            "confidence_score": 0.0,
            "drift_type": "",
            "attempt_count": 1,
            "max_retries": 3,
            "audit_log": {},
            "tdo_data": {},
            "error_message": "",
            "execution_start_ms": 0.0,
        }
        result = analyze_dom(state)
        assert result["status"] == HealingStatus.FAILED.value


class TestGenerateSelectorNode:
    """Tests for the generate_selector node in isolation."""

    def test_prefers_data_testid(self) -> None:
        from backend.graph.nodes.generate_selector import generate_selector

        state: HealingState = {
            "candidate_selectors": [{
                "element": {
                    "tag": "button",
                    "element_id": "btn",
                    "classes": ["btn"],
                    "text": "Click",
                    "attributes": {},
                    "data_testid": "my-btn",
                    "depth": 1,
                    "child_index": 0,
                    "xpath": "/html/body/button",
                    "parent_tag": "body",
                    "child_count": 0,
                },
                "composite_score": 95.0,
                "breakdown": {},
            }],
            "original_attributes": {"tag": "button", "classes": [], "attributes": {}},
            "status": HealingStatus.PENDING.value,
            "failure_payload": {},
            "dom_snapshot": "",
            "parsed_elements": [],
            "healed_selector": "",
            "healed_selector_type": "",
            "confidence_score": 0.0,
            "drift_type": "",
            "attempt_count": 1,
            "max_retries": 3,
            "audit_log": {},
            "tdo_data": {},
            "error_message": "",
            "execution_start_ms": 0.0,
        }
        result = generate_selector(state)
        assert result["healed_selector"] == '[data-testid="my-btn"]'
        assert result["healed_selector_type"] == SelectorType.DATA_TESTID.value

    def test_falls_back_to_id(self) -> None:
        from backend.graph.nodes.generate_selector import generate_selector

        state: HealingState = {
            "candidate_selectors": [{
                "element": {
                    "tag": "button",
                    "element_id": "submit",
                    "classes": ["btn"],
                    "text": "Click",
                    "attributes": {},
                    "data_testid": None,
                    "depth": 1,
                    "child_index": 0,
                    "xpath": "/html/body/button",
                    "parent_tag": "body",
                    "child_count": 0,
                },
                "composite_score": 90.0,
                "breakdown": {},
            }],
            "original_attributes": {"tag": "button", "classes": [], "attributes": {}},
            "status": HealingStatus.PENDING.value,
            "failure_payload": {},
            "dom_snapshot": "",
            "parsed_elements": [],
            "healed_selector": "",
            "healed_selector_type": "",
            "confidence_score": 0.0,
            "drift_type": "",
            "attempt_count": 1,
            "max_retries": 3,
            "audit_log": {},
            "tdo_data": {},
            "error_message": "",
            "execution_start_ms": 0.0,
        }
        result = generate_selector(state)
        assert result["healed_selector"] == "#submit"
        assert result["healed_selector_type"] == SelectorType.CSS.value


# ------------------------------------------------------------------
# Routing edge
# ------------------------------------------------------------------

class TestRouting:
    """Tests for the conditional routing logic."""

    def test_routes_to_rerun_on_heal(self) -> None:
        from backend.graph.edges.routing import route_after_validation

        state: HealingState = {
            "status": HealingStatus.HEALED.value,
            "confidence_score": 95.0,
            "attempt_count": 1,
            "max_retries": 3,
            "failure_payload": {},
            "dom_snapshot": "",
            "parsed_elements": [],
            "original_attributes": {},
            "candidate_selectors": [],
            "healed_selector": "#btn",
            "healed_selector_type": "css",
            "drift_type": "",
            "audit_log": {},
            "tdo_data": {},
            "error_message": "",
            "execution_start_ms": 0.0,
        }
        assert route_after_validation(state) == "rerun_test"

    def test_routes_to_retry(self) -> None:
        from backend.graph.edges.routing import route_after_validation

        state: HealingState = {
            "status": HealingStatus.VALIDATING.value,
            "confidence_score": 50.0,
            "attempt_count": 1,
            "max_retries": 3,
            "failure_payload": {},
            "dom_snapshot": "",
            "parsed_elements": [],
            "original_attributes": {},
            "candidate_selectors": [],
            "healed_selector": "#btn",
            "healed_selector_type": "css",
            "drift_type": "",
            "audit_log": {},
            "tdo_data": {},
            "error_message": "",
            "execution_start_ms": 0.0,
        }
        assert route_after_validation(state) == "generate_selector"

    def test_routes_to_escalate(self) -> None:
        from backend.graph.edges.routing import route_after_validation

        state: HealingState = {
            "status": HealingStatus.VALIDATING.value,
            "confidence_score": 50.0,
            "attempt_count": 3,
            "max_retries": 3,
            "failure_payload": {},
            "dom_snapshot": "",
            "parsed_elements": [],
            "original_attributes": {},
            "candidate_selectors": [],
            "healed_selector": "#btn",
            "healed_selector_type": "css",
            "drift_type": "",
            "audit_log": {},
            "tdo_data": {},
            "error_message": "",
            "execution_start_ms": 0.0,
        }
        assert route_after_validation(state) == "escalate"


# ------------------------------------------------------------------
# FastAPI endpoint
# ------------------------------------------------------------------

class TestHealEndpoint:
    """FastAPI /heal endpoint integration tests."""

    def test_health_check(self, fastapi_client: TestClient) -> None:
        resp = fastapi_client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_root(self, fastapi_client: TestClient) -> None:
        resp = fastapi_client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "operational"
        assert "version" in data

    def test_heal_endpoint(
        self,
        fastapi_client: TestClient,
        test_failure_payload: TestFailurePayload,
    ) -> None:
        payload = test_failure_payload.model_dump(mode="json")
        resp = fastapi_client.post("/heal", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["test_case_id"] == "TC-001"
        assert data["status"] in [s.value for s in HealingStatus]
        assert "healed_selector" in data
        assert "confidence" in data

    def test_heal_endpoint_invalid_payload(self, fastapi_client: TestClient) -> None:
        resp = fastapi_client.post("/heal", json={})
        assert resp.status_code == 422  # Validation error
