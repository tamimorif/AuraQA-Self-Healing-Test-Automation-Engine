"""
AuraQA Core Data Models & Schemas.

All TypedDict, Pydantic, and enum definitions for inter-system communication.
These models define the contracts between UiPath, LangGraph, Jira, and TDO.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Optional, TypedDict

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SelectorType(str, enum.Enum):
    """Supported selector types for element identification."""
    CSS = "css"
    XPATH = "xpath"
    DATA_TESTID = "data-testid"


class HealingStatus(str, enum.Enum):
    """Status of the healing pipeline execution."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    VALIDATING = "validating"
    HEALED = "healed"
    RETRYING = "retrying"
    ESCALATED = "escalated"
    FAILED = "failed"


class JiraPriority(str, enum.Enum):
    """Jira issue priority levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class DriftType(str, enum.Enum):
    """Types of DOM selector drift detected."""
    ID_RENAME = "id_rename"
    CLASS_SWAP = "class_swap"
    NESTING_CHANGE = "nesting_change"
    ATTRIBUTE_REMOVAL = "attribute_removal"
    TAG_CHANGE = "tag_change"
    TEXT_CHANGE = "text_change"
    SIBLING_REORDER = "sibling_reorder"
    COMPOUND_SHIFT = "compound_shift"


# ---------------------------------------------------------------------------
# Pydantic Models — DOM Elements
# ---------------------------------------------------------------------------

class DOMElement(BaseModel):
    """Parsed representation of a single DOM element."""
    tag: str = Field(..., description="HTML tag name (e.g., 'button', 'div')")
    element_id: Optional[str] = Field(None, description="Element ID attribute")
    classes: list[str] = Field(default_factory=list, description="CSS class list")
    text: str = Field("", description="Inner text content (trimmed)")
    attributes: dict[str, str] = Field(
        default_factory=dict,
        description="All HTML attributes as key-value pairs",
    )
    data_testid: Optional[str] = Field(None, description="data-testid attribute value")
    depth: int = Field(0, description="Nesting depth in DOM tree (0 = root)")
    child_index: int = Field(0, description="Index among siblings (0-based)")
    xpath: str = Field("", description="Computed XPath to this element")
    parent_tag: Optional[str] = Field(None, description="Parent element tag name")
    child_count: int = Field(0, description="Number of direct children")

    @field_validator("text", mode="before")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else ""


class OriginalElementAttributes(BaseModel):
    """Attributes of the original element that the broken selector targeted."""
    tag: str = Field(..., description="Original HTML tag")
    element_id: Optional[str] = Field(None, description="Original ID attribute")
    classes: list[str] = Field(default_factory=list, description="Original CSS classes")
    text: str = Field("", description="Original inner text")
    attributes: dict[str, str] = Field(
        default_factory=dict,
        description="Original HTML attributes",
    )
    data_testid: Optional[str] = Field(None, description="Original data-testid")
    depth: Optional[int] = Field(None, description="Original nesting depth")
    parent_tag: Optional[str] = Field(None, description="Original parent tag")


# ---------------------------------------------------------------------------
# Pydantic Models — UiPath ↔ Python Contracts
# ---------------------------------------------------------------------------

class TestFailurePayload(BaseModel):
    """
    Payload sent from UiPath to the Python healing agent upon test failure.
    Contract: UiPath → Python (POST /heal)
    """
    test_case_id: str = Field(..., description="Unique test case identifier")
    test_suite_id: str = Field(..., description="Parent test suite identifier")
    broken_selector: str = Field(..., description="CSS/XPath selector that failed")
    selector_type: SelectorType = Field(..., description="Type of the broken selector")
    dom_snapshot: str = Field(..., description="Full HTML of the page at failure time")
    original_element_attributes: OriginalElementAttributes = Field(
        ...,
        description="Known attributes of the element the selector originally matched",
    )
    page_url: str = Field(..., description="URL of the page under test")
    screenshot_base64: Optional[str] = Field(
        None,
        description="Base64-encoded screenshot at failure time",
    )
    error_message: str = Field("", description="UiPath error message on failure")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of the failure",
    )
    environment: str = Field("staging", description="Execution environment identifier")
    retry_count: int = Field(0, description="Number of prior healing attempts")

    @field_validator("dom_snapshot", mode="before")
    @classmethod
    def validate_dom_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("dom_snapshot must not be empty")
        return v


class CandidateSelector(BaseModel):
    """A candidate healed selector with confidence metadata."""
    selector: str = Field(..., description="Generated CSS or XPath selector")
    selector_type: SelectorType = Field(..., description="Type of selector")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Confidence score (0-100)",
    )
    matched_element: Optional[DOMElement] = Field(
        None,
        description="The DOM element this selector matches",
    )
    scoring_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Individual scoring factor values",
    )


class HealedSelectorResponse(BaseModel):
    """
    Payload returned from Python to UiPath with the healed selector.
    Contract: Python → UiPath (response to POST /heal)
    """
    test_case_id: str = Field(..., description="Original test case identifier")
    original_selector: str = Field(..., description="The broken selector")
    healed_selector: str = Field(..., description="New healed selector")
    healed_selector_type: SelectorType = Field(
        ...,
        description="Type of the healed selector",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Final confidence score (0-100)",
    )
    status: HealingStatus = Field(..., description="Final healing status")
    candidates_evaluated: int = Field(
        0,
        description="Number of candidate selectors evaluated",
    )
    top_candidates: list[CandidateSelector] = Field(
        default_factory=list,
        description="Top 3 candidate selectors considered",
    )
    drift_type: Optional[DriftType] = Field(
        None,
        description="Detected type of selector drift",
    )
    attempt_count: int = Field(1, description="Number of healing attempts made")
    execution_time_ms: float = Field(
        0.0,
        description="Total healing pipeline execution time in milliseconds",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of the healing response",
    )
    audit_log_id: Optional[str] = Field(
        None,
        description="Reference to the generated audit log entry",
    )


# ---------------------------------------------------------------------------
# Pydantic Models — Jira Audit
# ---------------------------------------------------------------------------

class AuditLogEntry(BaseModel):
    """Audit log entry for Jira issue creation."""
    audit_id: str = Field(..., description="Unique audit entry identifier")
    test_case_id: str = Field(..., description="Associated test case")
    test_suite_id: str = Field(..., description="Associated test suite")
    original_selector: str = Field(..., description="Broken selector")
    healed_selector: Optional[str] = Field(None, description="Healed selector if found")
    confidence: float = Field(0.0, description="Final confidence score")
    status: HealingStatus = Field(..., description="Final healing status")
    drift_type: Optional[DriftType] = Field(None, description="Detected drift type")
    attempt_count: int = Field(1, description="Total healing attempts")
    execution_time_ms: float = Field(0.0, description="Pipeline execution time")
    page_url: str = Field("", description="Page URL under test")
    environment: str = Field("staging", description="Execution environment")
    error_message: str = Field("", description="Error message if failed/escalated")
    scoring_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Detailed scoring factors",
    )
    jira_issue_key: Optional[str] = Field(
        None,
        description="Created Jira issue key (e.g., AURA-123)",
    )
    jira_priority: JiraPriority = Field(
        JiraPriority.MEDIUM,
        description="Jira issue priority",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp",
    )


# ---------------------------------------------------------------------------
# Pydantic Models — TDO (Test Data Orchestrator)
# ---------------------------------------------------------------------------

class TDORequest(BaseModel):
    """Request payload for TDO synthetic test data provisioning."""
    test_case_id: str = Field(..., description="Test case requiring data")
    dataset_name: str = Field(..., description="TDO dataset identifier")
    record_count: int = Field(1, ge=1, le=1000, description="Number of records")
    schema_fields: dict[str, str] = Field(
        default_factory=dict,
        description="Field name → data type mapping (e.g., {'email': 'email', 'name': 'full_name'})",
    )
    filters: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional filters for data generation",
    )
    environment: str = Field("staging", description="Target environment")


class TDOResponse(BaseModel):
    """Response from TDO with provisioned test data."""
    request_id: str = Field(..., description="TDO request tracking ID")
    test_case_id: str = Field(..., description="Associated test case")
    dataset_name: str = Field(..., description="Dataset identifier")
    records: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Provisioned test data records",
    )
    record_count: int = Field(0, description="Actual number of records returned")
    provisioned_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of provisioning",
    )


# ---------------------------------------------------------------------------
# TypedDict — LangGraph State
# ---------------------------------------------------------------------------

class HealingState(TypedDict, total=False):
    """
    LangGraph state object passed between all nodes in the healing pipeline.

    Fields:
        failure_payload: Deserialized test failure data from UiPath.
        dom_snapshot: Raw HTML string of the page.
        parsed_elements: List of all parsed DOM elements.
        original_attributes: Attributes of the original target element.
        candidate_selectors: Ranked list of candidate healed selectors.
        healed_selector: Final healed selector string.
        healed_selector_type: Type of the healed selector.
        confidence_score: Final confidence score (0-100).
        drift_type: Detected type of selector drift.
        attempt_count: Current healing attempt number.
        max_retries: Maximum retry attempts before escalation.
        status: Current pipeline status.
        audit_log: Constructed audit log entry.
        tdo_data: Provisioned test data from TDO.
        error_message: Error message if pipeline fails.
        execution_start_ms: Pipeline start timestamp in ms.
    """
    failure_payload: dict[str, Any]
    dom_snapshot: str
    parsed_elements: list[dict[str, Any]]
    original_attributes: dict[str, Any]
    candidate_selectors: list[dict[str, Any]]
    healed_selector: str
    healed_selector_type: str
    confidence_score: float
    drift_type: str
    attempt_count: int
    max_retries: int
    status: str
    audit_log: dict[str, Any]
    tdo_data: dict[str, Any]
    error_message: str
    execution_start_ms: float
