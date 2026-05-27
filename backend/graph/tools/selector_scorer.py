"""
Multi-factor element scoring for the AuraQA self-healing pipeline.

Compares each candidate DOM element against the original element's known
attributes using five weighted factors.
"""
from __future__ import annotations

import logging
from difflib import SequenceMatcher
from dataclasses import dataclass

from backend.models.schemas import DOMElement, OriginalElementAttributes

logger = logging.getLogger(__name__)

# Scoring weights — MUST sum to 1.0
WEIGHT_TEXT = 0.35
WEIGHT_ATTRIBUTE = 0.25
WEIGHT_TAG = 0.15
WEIGHT_STRUCTURAL = 0.15
WEIGHT_ID = 0.10


@dataclass(frozen=True)
class ScoringResult:
    """Detailed breakdown of an element's composite score."""
    element: DOMElement
    text_score: float
    attribute_score: float
    tag_score: float
    structural_score: float
    id_score: float
    composite: float

    @property
    def breakdown(self) -> dict[str, float]:
        return {
            "text_similarity": round(self.text_score, 4),
            "attribute_overlap": round(self.attribute_score, 4),
            "tag_match": round(self.tag_score, 4),
            "structural_proximity": round(self.structural_score, 4),
            "id_similarity": round(self.id_score, 4),
            "composite": round(self.composite, 4),
        }


class SelectorScorer:
    """
    Scores candidate DOM elements against the original element attributes.

    Scoring factors and weights:
        - text_similarity:      SequenceMatcher ratio × 0.35
        - attribute_overlap:    Jaccard similarity   × 0.25
        - tag_match:            exact tag match      × 0.15
        - structural_proximity: 1/(1+|Δdepth|)      × 0.15
        - id_similarity:        SequenceMatcher ratio× 0.10
    """

    def __init__(
        self,
        *,
        weight_text: float = WEIGHT_TEXT,
        weight_attribute: float = WEIGHT_ATTRIBUTE,
        weight_tag: float = WEIGHT_TAG,
        weight_structural: float = WEIGHT_STRUCTURAL,
        weight_id: float = WEIGHT_ID,
    ) -> None:
        self.w_text = weight_text
        self.w_attr = weight_attribute
        self.w_tag = weight_tag
        self.w_struct = weight_structural
        self.w_id = weight_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def score_all(
        self,
        candidates: list[DOMElement],
        original: OriginalElementAttributes,
    ) -> list[ScoringResult]:
        """Score every candidate and return sorted (descending) results."""
        results = [self._score_one(elem, original) for elem in candidates]
        results.sort(key=lambda r: r.composite, reverse=True)
        return results

    def top_n(
        self,
        candidates: list[DOMElement],
        original: OriginalElementAttributes,
        n: int = 3,
    ) -> list[ScoringResult]:
        """Return the top *n* scoring results."""
        return self.score_all(candidates, original)[:n]

    # ------------------------------------------------------------------
    # Individual scoring factors
    # ------------------------------------------------------------------

    @staticmethod
    def _text_similarity(candidate_text: str, original_text: str) -> float:
        """SequenceMatcher ratio on text content."""
        if not candidate_text and not original_text:
            return 1.0
        if not candidate_text or not original_text:
            return 0.0
        return SequenceMatcher(None, candidate_text.lower(), original_text.lower()).ratio()

    @staticmethod
    def _attribute_overlap(
        cand_attrs: dict[str, str],
        cand_classes: list[str],
        orig_attrs: dict[str, str],
        orig_classes: list[str],
    ) -> float:
        """Jaccard similarity on the union of attributes and classes."""
        cand_set: set[str] = set()
        orig_set: set[str] = set()

        for k, v in cand_attrs.items():
            cand_set.add(f"{k}={v}")
        for cls in cand_classes:
            cand_set.add(f"class={cls}")

        for k, v in orig_attrs.items():
            orig_set.add(f"{k}={v}")
        for cls in orig_classes:
            orig_set.add(f"class={cls}")

        if not cand_set and not orig_set:
            return 1.0
        if not cand_set or not orig_set:
            return 0.0

        intersection = cand_set & orig_set
        union = cand_set | orig_set
        return len(intersection) / len(union)

    @staticmethod
    def _tag_match(candidate_tag: str, original_tag: str) -> float:
        """Binary: 1.0 if same tag, 0.0 otherwise."""
        return 1.0 if candidate_tag.lower() == original_tag.lower() else 0.0

    @staticmethod
    def _structural_proximity(candidate_depth: int, original_depth: int | None) -> float:
        """Inverse absolute depth difference."""
        if original_depth is None:
            return 0.5  # neutral when unknown
        return 1.0 / (1.0 + abs(original_depth - candidate_depth))

    @staticmethod
    def _id_similarity(candidate_id: str | None, original_id: str | None) -> float:
        """SequenceMatcher ratio on ID attributes."""
        if not candidate_id and not original_id:
            return 1.0
        if not candidate_id or not original_id:
            return 0.0
        return SequenceMatcher(None, candidate_id.lower(), original_id.lower()).ratio()

    # ------------------------------------------------------------------
    # Composite
    # ------------------------------------------------------------------

    def _score_one(
        self,
        elem: DOMElement,
        orig: OriginalElementAttributes,
    ) -> ScoringResult:
        text_s = self._text_similarity(elem.text, orig.text)
        attr_s = self._attribute_overlap(
            elem.attributes, elem.classes, orig.attributes, orig.classes,
        )
        tag_s = self._tag_match(elem.tag, orig.tag)
        struct_s = self._structural_proximity(elem.depth, orig.depth)
        id_s = self._id_similarity(elem.element_id, orig.element_id)

        composite = (
            text_s * self.w_text
            + attr_s * self.w_attr
            + tag_s * self.w_tag
            + struct_s * self.w_struct
            + id_s * self.w_id
        )
        # Scale to 0-100
        composite_pct = round(composite * 100, 2)

        return ScoringResult(
            element=elem,
            text_score=round(text_s * self.w_text * 100, 2),
            attribute_score=round(attr_s * self.w_attr * 100, 2),
            tag_score=round(tag_s * self.w_tag * 100, 2),
            structural_score=round(struct_s * self.w_struct * 100, 2),
            id_score=round(id_s * self.w_id * 100, 2),
            composite=composite_pct,
        )
