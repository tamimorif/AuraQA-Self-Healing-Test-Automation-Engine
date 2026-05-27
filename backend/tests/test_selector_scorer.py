"""
Unit tests for the SelectorScorer.
"""
from __future__ import annotations

import pytest

from backend.graph.tools.selector_scorer import SelectorScorer, ScoringResult
from backend.models.schemas import DOMElement, OriginalElementAttributes


class TestSelectorScorer:
    """SelectorScorer unit tests."""

    def setup_method(self) -> None:
        self.scorer = SelectorScorer()

    @pytest.fixture
    def exact_match_element(self) -> DOMElement:
        """Element that exactly matches the original attributes."""
        return DOMElement(
            tag="button",
            element_id="submit-btn",
            classes=["btn", "primary"],
            text="Sign In",
            attributes={"type": "submit"},
            data_testid="submit-btn",
            depth=3,
            child_index=4,
            xpath="/html/body/div/main/form/button",
            parent_tag="form",
        )

    @pytest.fixture
    def partial_match_element(self) -> DOMElement:
        """Element that partially matches — drifted ID and text."""
        return DOMElement(
            tag="button",
            element_id="login-btn",
            classes=["btn", "btn-primary"],
            text="Log In",
            attributes={"type": "submit"},
            data_testid="login-btn",
            depth=3,
            child_index=4,
            xpath="/html/body/div/main/form/button",
            parent_tag="form",
        )

    @pytest.fixture
    def no_match_element(self) -> DOMElement:
        """Element that does not match at all."""
        return DOMElement(
            tag="span",
            element_id="footer-text",
            classes=["footer"],
            text="© 2026 AuraQA",
            attributes={},
            depth=1,
            child_index=0,
            xpath="/html/body/div/footer/span",
            parent_tag="footer",
        )

    def test_exact_match_scores_high(
        self,
        exact_match_element: DOMElement,
        original_attributes: OriginalElementAttributes,
    ) -> None:
        results = self.scorer.score_all([exact_match_element], original_attributes)
        assert len(results) == 1
        assert results[0].composite >= 90.0

    def test_partial_match_scores_moderate(
        self,
        partial_match_element: DOMElement,
        original_attributes: OriginalElementAttributes,
    ) -> None:
        results = self.scorer.score_all([partial_match_element], original_attributes)
        assert len(results) == 1
        # Should score lower than exact but still reasonable
        assert 30.0 < results[0].composite < 90.0

    def test_no_match_scores_low(
        self,
        no_match_element: DOMElement,
        original_attributes: OriginalElementAttributes,
    ) -> None:
        results = self.scorer.score_all([no_match_element], original_attributes)
        assert len(results) == 1
        assert results[0].composite < 40.0

    def test_ranking_order(
        self,
        exact_match_element: DOMElement,
        partial_match_element: DOMElement,
        no_match_element: DOMElement,
        original_attributes: OriginalElementAttributes,
    ) -> None:
        candidates = [no_match_element, partial_match_element, exact_match_element]
        results = self.scorer.score_all(candidates, original_attributes)
        # Best match should be first
        assert results[0].element.element_id == "submit-btn"
        assert results[-1].element.element_id == "footer-text"
        # Scores should be descending
        scores = [r.composite for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_top_n(
        self,
        exact_match_element: DOMElement,
        partial_match_element: DOMElement,
        no_match_element: DOMElement,
        original_attributes: OriginalElementAttributes,
    ) -> None:
        candidates = [no_match_element, partial_match_element, exact_match_element]
        top = self.scorer.top_n(candidates, original_attributes, n=2)
        assert len(top) == 2
        assert top[0].composite >= top[1].composite

    def test_breakdown_contains_all_factors(
        self,
        exact_match_element: DOMElement,
        original_attributes: OriginalElementAttributes,
    ) -> None:
        results = self.scorer.score_all([exact_match_element], original_attributes)
        breakdown = results[0].breakdown
        expected_keys = {
            "text_similarity",
            "attribute_overlap",
            "tag_match",
            "structural_proximity",
            "id_similarity",
            "composite",
        }
        assert set(breakdown.keys()) == expected_keys

    def test_empty_candidates(
        self,
        original_attributes: OriginalElementAttributes,
    ) -> None:
        results = self.scorer.score_all([], original_attributes)
        assert results == []

    def test_text_similarity_identical(self) -> None:
        score = SelectorScorer._text_similarity("Sign In", "Sign In")
        assert score == 1.0

    def test_text_similarity_empty_both(self) -> None:
        score = SelectorScorer._text_similarity("", "")
        assert score == 1.0

    def test_text_similarity_one_empty(self) -> None:
        score = SelectorScorer._text_similarity("Hello", "")
        assert score == 0.0

    def test_tag_match_same(self) -> None:
        assert SelectorScorer._tag_match("button", "button") == 1.0

    def test_tag_match_different(self) -> None:
        assert SelectorScorer._tag_match("button", "div") == 0.0

    def test_tag_match_case_insensitive(self) -> None:
        assert SelectorScorer._tag_match("BUTTON", "button") == 1.0

    def test_structural_proximity_same_depth(self) -> None:
        assert SelectorScorer._structural_proximity(3, 3) == 1.0

    def test_structural_proximity_different_depth(self) -> None:
        score = SelectorScorer._structural_proximity(3, 5)
        assert 0.0 < score < 1.0

    def test_structural_proximity_none_depth(self) -> None:
        score = SelectorScorer._structural_proximity(3, None)
        assert score == 0.5

    def test_id_similarity_identical(self) -> None:
        assert SelectorScorer._id_similarity("submit-btn", "submit-btn") == 1.0

    def test_id_similarity_both_none(self) -> None:
        assert SelectorScorer._id_similarity(None, None) == 1.0

    def test_id_similarity_one_none(self) -> None:
        assert SelectorScorer._id_similarity("submit-btn", None) == 0.0

    def test_attribute_overlap_identical(self) -> None:
        attrs = {"type": "submit"}
        classes = ["btn", "primary"]
        score = SelectorScorer._attribute_overlap(attrs, classes, attrs, classes)
        assert score == 1.0

    def test_attribute_overlap_disjoint(self) -> None:
        score = SelectorScorer._attribute_overlap(
            {"type": "submit"}, ["btn"],
            {"name": "field"}, ["input"],
        )
        assert score == 0.0

    def test_attribute_overlap_partial(self) -> None:
        score = SelectorScorer._attribute_overlap(
            {"type": "submit"}, ["btn", "primary"],
            {"type": "submit"}, ["btn", "secondary"],
        )
        assert 0.0 < score < 1.0

    def test_custom_weights(
        self,
        exact_match_element: DOMElement,
        original_attributes: OriginalElementAttributes,
    ) -> None:
        """Scorer should accept custom weights."""
        scorer = SelectorScorer(
            weight_text=0.5,
            weight_attribute=0.2,
            weight_tag=0.1,
            weight_structural=0.1,
            weight_id=0.1,
        )
        results = scorer.score_all([exact_match_element], original_attributes)
        assert len(results) == 1
        assert results[0].composite > 0
