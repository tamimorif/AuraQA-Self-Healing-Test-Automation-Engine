"""
Schema validation tests for AuraQA Pydantic models.
"""
from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from backend.models.schemas import (
    AuditLogEntry,
    CandidateSelector,
    DOMElement,
    DriftType,
    HealedSelectorResponse,
    HealingStatus,
    JiraPriority,
    OriginalElementAttributes,
    SelectorType,
    TDORequest,
    TDOResponse,
    TestFailurePayload,
)


# ------------------------------------------------------------------
# DOMElement
# ------------------------------------------------------------------

class TestDOMElement:
    """DOMElement validation tests."""

    def test_create_minimal(self) -> None:
        elem = DOMElement(tag="div")
        assert elem.tag == "div"
        assert elem.element_id is None
        assert elem.classes == []
        assert elem.text == ""
        assert elem.depth == 0

    def test_create_full(self, sample_dom_element: DOMElement) -> None:
        assert sample_dom_element.tag == "button"
        assert sample_dom_element.element_id == "submit-btn"
        assert "btn" in sample_dom_element.classes
        assert sample_dom_element.data_testid == "submit-btn"

    def test_text_strip(self) -> None:
        elem = DOMElement(tag="span", text="  hello world  ")
        assert elem.text == "hello world"

    def test_text_non_string_defaults(self) -> None:
        elem = DOMElement(tag="span", text=None)  # type: ignore[arg-type]
        assert elem.text == ""


# ------------------------------------------------------------------
# OriginalElementAttributes
# ------------------------------------------------------------------

class TestOriginalElementAttributes:
    """OriginalElementAttributes validation tests."""

    def test_create(self) -> None:
        attrs = OriginalElementAttributes(
            tag="input",
            element_id="email",
            classes=["input"],
            text="",
            attributes={"type": "email"},
        )
        assert attrs.tag == "input"
        assert attrs.element_id == "email"

    def test_optional_depth(self) -> None:
        attrs = OriginalElementAttributes(tag="div")
        assert attrs.depth is None


# ------------------------------------------------------------------
# TestFailurePayload
# ------------------------------------------------------------------

class TestTestFailurePayload:
    """TestFailurePayload validation tests."""

    def test_valid_payload(self, test_failure_payload: TestFailurePayload) -> None:
        assert test_failure_payload.test_case_id == "TC-001"
        assert test_failure_payload.selector_type == SelectorType.CSS
        assert len(test_failure_payload.dom_snapshot) > 0

    def test_empty_dom_raises(self) -> None:
        with pytest.raises(ValidationError, match="dom_snapshot must not be empty"):
            TestFailurePayload(
                test_case_id="TC-X",
                test_suite_id="TS-X",
                broken_selector="#x",
                selector_type=SelectorType.CSS,
                dom_snapshot="",
                original_element_attributes=OriginalElementAttributes(tag="div"),
                page_url="http://example.com",
            )

    def test_whitespace_dom_raises(self) -> None:
        with pytest.raises(ValidationError, match="dom_snapshot must not be empty"):
            TestFailurePayload(
                test_case_id="TC-X",
                test_suite_id="TS-X",
                broken_selector="#x",
                selector_type=SelectorType.CSS,
                dom_snapshot="   \n  ",
                original_element_attributes=OriginalElementAttributes(tag="div"),
                page_url="http://example.com",
            )

    def test_default_timestamp(self, test_failure_payload: TestFailurePayload) -> None:
        assert isinstance(test_failure_payload.timestamp, datetime)


# ------------------------------------------------------------------
# CandidateSelector
# ------------------------------------------------------------------

class TestCandidateSelector:
    """CandidateSelector validation tests."""

    def test_create(self) -> None:
        cs = CandidateSelector(
            selector="#submit-btn",
            selector_type=SelectorType.CSS,
            confidence=95.5,
        )
        assert cs.confidence == 95.5

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            CandidateSelector(
                selector="#x",
                selector_type=SelectorType.CSS,
                confidence=101.0,
            )

        with pytest.raises(ValidationError):
            CandidateSelector(
                selector="#x",
                selector_type=SelectorType.CSS,
                confidence=-1.0,
            )


# ------------------------------------------------------------------
# HealedSelectorResponse
# ------------------------------------------------------------------

class TestHealedSelectorResponse:
    """HealedSelectorResponse validation tests."""

    def test_create(self) -> None:
        resp = HealedSelectorResponse(
            test_case_id="TC-001",
            original_selector="#old",
            healed_selector="#new",
            healed_selector_type=SelectorType.CSS,
            confidence=90.0,
            status=HealingStatus.HEALED,
        )
        assert resp.status == HealingStatus.HEALED
        assert resp.confidence == 90.0

    def test_drift_type_optional(self) -> None:
        resp = HealedSelectorResponse(
            test_case_id="TC-001",
            original_selector="#old",
            healed_selector="#new",
            healed_selector_type=SelectorType.CSS,
            confidence=85.0,
            status=HealingStatus.HEALED,
        )
        assert resp.drift_type is None


# ------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------

class TestEnums:
    """Enum value tests."""

    def test_selector_type_values(self) -> None:
        assert SelectorType.CSS.value == "css"
        assert SelectorType.XPATH.value == "xpath"
        assert SelectorType.DATA_TESTID.value == "data-testid"

    def test_healing_status_values(self) -> None:
        assert HealingStatus.HEALED.value == "healed"
        assert HealingStatus.ESCALATED.value == "escalated"

    def test_drift_type_values(self) -> None:
        assert DriftType.ID_RENAME.value == "id_rename"
        assert DriftType.COMPOUND_SHIFT.value == "compound_shift"

    def test_jira_priority_values(self) -> None:
        assert JiraPriority.CRITICAL.value == "Critical"
        assert JiraPriority.LOW.value == "Low"


# ------------------------------------------------------------------
# TDO models
# ------------------------------------------------------------------

class TestTDOModels:
    """TDO request/response validation tests."""

    def test_tdo_request(self) -> None:
        req = TDORequest(
            test_case_id="TC-001",
            dataset_name="users",
            record_count=5,
            schema_fields={"email": "email", "name": "full_name"},
        )
        assert req.record_count == 5

    def test_tdo_request_bounds(self) -> None:
        with pytest.raises(ValidationError):
            TDORequest(
                test_case_id="TC-X",
                dataset_name="x",
                record_count=0,
            )

    def test_tdo_response(self) -> None:
        resp = TDOResponse(
            request_id="req-1",
            test_case_id="TC-001",
            dataset_name="users",
            records=[{"email": "a@b.com"}],
            record_count=1,
        )
        assert resp.record_count == 1
        assert len(resp.records) == 1


# ------------------------------------------------------------------
# AuditLogEntry
# ------------------------------------------------------------------

class TestAuditLogEntry:
    """AuditLogEntry validation tests."""

    def test_create(self) -> None:
        entry = AuditLogEntry(
            audit_id="aud-1",
            test_case_id="TC-001",
            test_suite_id="TS-LOGIN",
            original_selector="#old",
            status=HealingStatus.HEALED,
            confidence=92.0,
        )
        assert entry.jira_priority == JiraPriority.MEDIUM
        assert entry.jira_issue_key is None
