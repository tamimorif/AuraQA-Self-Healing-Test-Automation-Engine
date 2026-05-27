"""
LangGraph node: generate a healed CSS / XPath selector.

Examines the top-ranked candidate element and produces the most specific
selector possible using the preference hierarchy:

    data-testid  →  ID  →  class combination  →  nth-child XPath
"""
from __future__ import annotations

import logging
from typing import Any

from backend.graph.state import HealingState
from backend.models.schemas import DOMElement, HealingStatus, SelectorType

logger = logging.getLogger(__name__)


def generate_selector(state: HealingState) -> HealingState:
    """
    Generate a healed selector from the highest-scoring candidate.

    Updates:
        - ``healed_selector``
        - ``healed_selector_type``
        - ``confidence_score``
        - ``status`` → GENERATING
    """
    logger.info("generate_selector — building healed selector")
    state["status"] = HealingStatus.GENERATING.value

    candidates = state.get("candidate_selectors", [])
    if not candidates:
        state["error_message"] = "No candidate elements available for selector generation"
        state["status"] = HealingStatus.FAILED.value
        return state

    best = candidates[0]
    elem_data: dict[str, Any] = best["element"]
    composite_score: float = best["composite_score"]
    elem = DOMElement(**elem_data)

    selector, selector_type = _build_selector(elem)

    state["healed_selector"] = selector
    state["healed_selector_type"] = selector_type.value
    state["confidence_score"] = composite_score

    # Detect drift type
    drift = _detect_drift(state["original_attributes"], elem_data)
    if drift:
        state["drift_type"] = drift

    logger.info(
        "generate_selector — selector=%s type=%s confidence=%.2f drift=%s",
        selector,
        selector_type.value,
        composite_score,
        drift or "none",
    )
    return state


# ------------------------------------------------------------------
# Selector construction helpers
# ------------------------------------------------------------------

def _build_selector(elem: DOMElement) -> tuple[str, SelectorType]:
    """Return the most specific selector + its type for the element."""

    # 1. data-testid  (most reliable)
    if elem.data_testid:
        return f'[data-testid="{elem.data_testid}"]', SelectorType.DATA_TESTID

    # 2. ID  (unique per spec)
    if elem.element_id:
        return f"#{elem.element_id}", SelectorType.CSS

    # 3. Class combination  (prefer multi-class for specificity)
    if elem.classes:
        class_part = ".".join(elem.classes)
        css = f"{elem.tag}.{class_part}"
        return css, SelectorType.CSS

    # 4. XPath nth-child fallback
    if elem.xpath:
        return elem.xpath, SelectorType.XPATH

    # 5. Absolute fallback — tag + child index
    fallback = f"{elem.tag}:nth-child({elem.child_index + 1})"
    return fallback, SelectorType.CSS


def _detect_drift(
    original_raw: dict[str, Any],
    candidate_raw: dict[str, Any],
) -> str:
    """Heuristically classify the type of selector drift."""

    orig_id = original_raw.get("element_id") or ""
    cand_id = candidate_raw.get("element_id") or ""
    orig_tag = original_raw.get("tag", "")
    cand_tag = candidate_raw.get("tag", "")
    orig_classes = set(original_raw.get("classes", []))
    cand_classes = set(candidate_raw.get("classes", []))
    orig_depth = original_raw.get("depth")
    cand_depth = candidate_raw.get("depth", 0)
    orig_text = original_raw.get("text", "")
    cand_text = candidate_raw.get("text", "")
    orig_attrs = set(original_raw.get("attributes", {}).keys())
    cand_attrs = set(candidate_raw.get("attributes", {}).keys())

    drifts: list[str] = []

    if orig_id and cand_id and orig_id != cand_id:
        drifts.append("id_rename")
    elif orig_id and not cand_id:
        drifts.append("attribute_removal")

    if orig_tag != cand_tag:
        drifts.append("tag_change")

    if orig_classes != cand_classes and orig_classes:
        drifts.append("class_swap")

    if orig_depth is not None and cand_depth != orig_depth:
        drifts.append("nesting_change")

    if orig_text and cand_text and orig_text != cand_text:
        drifts.append("text_change")

    if orig_attrs - cand_attrs:
        drifts.append("attribute_removal")

    if len(drifts) >= 3:
        return "compound_shift"
    if drifts:
        return drifts[0]
    return ""
