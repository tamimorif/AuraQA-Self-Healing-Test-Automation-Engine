"""
LangGraph node: analyse the DOM snapshot.

Parses the raw HTML into structured ``DOMElement`` objects and scores
every element against the original element's known attributes.
"""
from __future__ import annotations

import logging

from backend.graph.state import HealingState
from backend.graph.tools.dom_parser import DOMParser
from backend.graph.tools.selector_scorer import SelectorScorer
from backend.models.schemas import HealingStatus, OriginalElementAttributes

logger = logging.getLogger(__name__)


def analyze_dom(state: HealingState) -> HealingState:
    """
    Parse the DOM snapshot and score each element.

    Updates:
        - ``parsed_elements``
        - ``candidate_selectors`` (top-3 scored elements as dicts)
        - ``status`` → ANALYZING
    """
    logger.info("analyze_dom — parsing DOM snapshot")
    state["status"] = HealingStatus.ANALYZING.value

    dom_snapshot = state["dom_snapshot"]
    original_attrs_raw = state["original_attributes"]
    original_attrs = OriginalElementAttributes(**original_attrs_raw)

    # 1. Parse HTML → DOMElement list
    parser = DOMParser()
    elements = parser.parse_html(dom_snapshot)
    state["parsed_elements"] = [e.model_dump(mode="json") for e in elements]

    if not elements:
        logger.warning("analyze_dom — no elements found in DOM snapshot")
        state["error_message"] = "No elements found in DOM snapshot"
        state["status"] = HealingStatus.FAILED.value
        return state

    # 2. Score all elements
    scorer = SelectorScorer()
    top_results = scorer.top_n(elements, original_attrs, n=3)

    # 3. Store top candidates with scoring metadata
    candidates: list[dict] = []
    for result in top_results:
        candidates.append({
            "element": result.element.model_dump(mode="json"),
            "composite_score": result.composite,
            "breakdown": result.breakdown,
        })
        logger.debug(
            "  candidate tag=%s id=%s score=%.2f",
            result.element.tag,
            result.element.element_id,
            result.composite,
        )

    state["candidate_selectors"] = candidates
    logger.info(
        "analyze_dom — found %d elements, top score %.2f",
        len(elements),
        top_results[0].composite if top_results else 0.0,
    )
    return state
