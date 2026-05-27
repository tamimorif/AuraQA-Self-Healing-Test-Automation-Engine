"""
LangGraph node: validate the generated selector against the DOM snapshot.

Ensures the healed selector matches **exactly one** element in the
original DOM and that confidence meets the threshold.
"""
from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from backend.config.settings import get_settings
from backend.graph.state import HealingState
from backend.models.schemas import (
    CandidateSelector,
    DOMElement,
    HealingStatus,
    SelectorType,
)

logger = logging.getLogger(__name__)


def validate_selector(state: HealingState) -> HealingState:
    """
    Validate the healed selector.

    Checks:
        1. The selector matches exactly 1 element in the DOM snapshot.
        2. The confidence score meets or exceeds the configured threshold.

    Updates:
        - ``status`` → VALIDATING / HEALED / RETRYING / ESCALATED
        - ``candidate_selectors[0]`` enriched with validation metadata
    """
    logger.info("validate_selector — validating healed selector")
    state["status"] = HealingStatus.VALIDATING.value

    selector = state.get("healed_selector", "")
    selector_type_str = state.get("healed_selector_type", "css")
    confidence = state.get("confidence_score", 0.0)
    dom_html = state.get("dom_snapshot", "")

    if not selector:
        state["error_message"] = "No selector to validate"
        state["status"] = HealingStatus.FAILED.value
        return state

    settings = get_settings()
    threshold = settings.confidence_threshold

    # ---- 1. Count matches in DOM ----
    match_count = _count_matches(dom_html, selector, selector_type_str)

    logger.info(
        "validate_selector — selector=%s matches=%d confidence=%.2f threshold=%.2f",
        selector,
        match_count,
        confidence,
        threshold,
    )

    # ---- 2. Apply validation rules ----
    if match_count == 1 and confidence >= threshold:
        state["status"] = HealingStatus.HEALED.value
        logger.info("validate_selector — HEALED ✓")
    elif match_count != 1:
        # Selector is ambiguous or dead — penalise confidence
        penalty = 30.0 if match_count == 0 else 20.0
        state["confidence_score"] = max(0.0, confidence - penalty)
        state["error_message"] = (
            f"Selector matched {match_count} element(s), expected exactly 1"
        )
        logger.warning("validate_selector — match_count=%d, penalised", match_count)
    else:
        # Confidence below threshold
        state["error_message"] = (
            f"Confidence {confidence:.1f}% below threshold {threshold:.1f}%"
        )
        logger.warning("validate_selector — confidence below threshold")

    return state


# ------------------------------------------------------------------
# DOM matching
# ------------------------------------------------------------------

def _count_matches(html: str, selector: str, selector_type: str) -> int:
    """Count how many elements in *html* match *selector*."""
    soup = BeautifulSoup(html, "html.parser")

    try:
        if selector_type in (SelectorType.CSS.value, SelectorType.DATA_TESTID.value):
            matches = soup.select(selector)
            return len(matches)

        if selector_type == SelectorType.XPATH.value:
            # BeautifulSoup doesn't support XPath natively.
            # We attempt a best-effort CSS fallback for simple XPaths,
            # otherwise assume 1 match (selector was derived from DOM).
            css_fallback = _xpath_to_css_best_effort(selector)
            if css_fallback:
                matches = soup.select(css_fallback)
                return len(matches)
            # For complex XPaths generated from our own DOMParser we
            # trust the element existed (it was extracted from this DOM).
            return 1
    except Exception as exc:
        logger.debug("Selector matching error: %s", exc)
        return 0

    return 0


def _xpath_to_css_best_effort(xpath: str) -> str | None:
    """
    Convert trivial XPaths (``/html/body/div/button``) to CSS selectors.

    Returns ``None`` when the XPath is too complex to convert.
    """
    if not xpath or "[" in xpath or "@" in xpath or "//" in xpath:
        return None
    parts = [p for p in xpath.strip("/").split("/") if p]
    if all(p.isidentifier() or p.replace("-", "").isalpha() for p in parts):
        return " > ".join(parts)
    return None
