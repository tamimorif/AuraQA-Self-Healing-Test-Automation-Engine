"""
Unit tests for the DOMParser.
"""
from __future__ import annotations

import pytest

from backend.graph.tools.dom_parser import DOMParser
from backend.models.schemas import DOMElement


class TestDOMParser:
    """DOMParser unit tests."""

    def setup_method(self) -> None:
        self.parser = DOMParser()

    def test_parse_basic_html(self, sample_dom: str) -> None:
        """Parser should extract multiple elements from sample DOM."""
        elements = self.parser.parse_html(sample_dom)
        assert len(elements) > 0
        tags = {e.tag for e in elements}
        assert "button" in tags
        assert "input" in tags
        assert "form" in tags

    def test_extract_elements_alias(self, sample_dom: str) -> None:
        """extract_elements should be an alias for parse_html."""
        a = self.parser.parse_html(sample_dom)
        b = self.parser.extract_elements(sample_dom)
        assert len(a) == len(b)

    def test_skips_script_and_style(self) -> None:
        html = "<body><script>var x=1;</script><style>.a{}</style><div>Hi</div></body>"
        elements = self.parser.parse_html(html)
        tags = {e.tag for e in elements}
        assert "script" not in tags
        assert "style" not in tags
        assert "div" in tags

    def test_element_id_extraction(self, sample_dom: str) -> None:
        elements = self.parser.parse_html(sample_dom)
        ids = {e.element_id for e in elements if e.element_id}
        assert "submit-btn" in ids
        assert "email" in ids
        assert "login-form" in ids

    def test_data_testid_extraction(self, sample_dom: str) -> None:
        elements = self.parser.parse_html(sample_dom)
        testids = {e.data_testid for e in elements if e.data_testid}
        assert "submit-btn" in testids
        assert "email-input" in testids
        assert "login-form" in testids

    def test_class_extraction(self, sample_dom: str) -> None:
        elements = self.parser.parse_html(sample_dom)
        btn = next(e for e in elements if e.element_id == "submit-btn")
        assert "btn" in btn.classes
        assert "primary" in btn.classes

    def test_text_extraction(self, sample_dom: str) -> None:
        elements = self.parser.parse_html(sample_dom)
        btn = next(e for e in elements if e.element_id == "submit-btn")
        assert "Sign In" in btn.text

    def test_depth_tracking(self, sample_dom: str) -> None:
        elements = self.parser.parse_html(sample_dom)
        # The top-level div#app should have depth 0
        app_div = next(e for e in elements if e.element_id == "app")
        assert app_div.depth == 0
        # Deeper elements should have depth > 0
        btn = next(e for e in elements if e.element_id == "submit-btn")
        assert btn.depth > 0

    def test_xpath_computation(self, sample_dom: str) -> None:
        elements = self.parser.parse_html(sample_dom)
        for elem in elements:
            assert elem.xpath.startswith("/")
            assert elem.tag in elem.xpath

    def test_parent_tag_tracking(self, sample_dom: str) -> None:
        elements = self.parser.parse_html(sample_dom)
        btn = next(e for e in elements if e.element_id == "submit-btn")
        assert btn.parent_tag == "form"

    def test_empty_html(self) -> None:
        elements = self.parser.parse_html("<html><body></body></html>")
        assert elements == []

    def test_nested_structure(self) -> None:
        html = """
        <body>
          <div id="outer">
            <div id="inner">
              <span id="deep">Text</span>
            </div>
          </div>
        </body>
        """
        elements = self.parser.parse_html(html)
        outer = next(e for e in elements if e.element_id == "outer")
        inner = next(e for e in elements if e.element_id == "inner")
        deep = next(e for e in elements if e.element_id == "deep")
        assert inner.depth > outer.depth
        assert deep.depth > inner.depth

    def test_child_count(self, sample_dom: str) -> None:
        elements = self.parser.parse_html(sample_dom)
        form = next(e for e in elements if e.element_id == "login-form")
        assert form.child_count > 0

    def test_attributes_excludes_class(self, sample_dom: str) -> None:
        """The 'class' attribute should not appear in the attributes dict."""
        elements = self.parser.parse_html(sample_dom)
        for elem in elements:
            assert "class" not in elem.attributes
