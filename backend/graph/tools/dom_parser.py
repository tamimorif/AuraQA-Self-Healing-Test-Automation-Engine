"""
DOM parsing utilities for the AuraQA self-healing pipeline.

Parses raw HTML snapshots into structured DOMElement objects using
BeautifulSoup, computing XPath, nesting depth, and sibling indices.
"""
from __future__ import annotations

import logging
from collections import Counter
from typing import Optional

from bs4 import BeautifulSoup, NavigableString, Tag

from backend.models.schemas import DOMElement

logger = logging.getLogger(__name__)

# Tags that never carry meaningful UI selectors
_SKIP_TAGS = frozenset({
    "html", "head", "meta", "link", "style", "script", "noscript",
    "title", "br", "hr", "col", "colgroup", "base",
})


class DOMParser:
    """
    Parses raw HTML into a flat list of ``DOMElement`` objects.

    Each element is enriched with:
    - Computed XPath
    - Nesting depth (0 = top-level body children)
    - Sibling (child) index
    - Parent tag name
    """

    def __init__(self, *, skip_tags: frozenset[str] | None = None) -> None:
        self._skip_tags = skip_tags or _SKIP_TAGS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_html(self, html: str) -> list[DOMElement]:
        """Parse a full HTML document and return all meaningful elements."""
        soup = BeautifulSoup(html, "html.parser")
        elements: list[DOMElement] = []
        body = soup.body or soup
        self._walk(body, elements, depth=0, parent_tag=None)
        logger.info("Parsed %d DOM elements from snapshot", len(elements))
        return elements

    def extract_elements(self, html: str) -> list[DOMElement]:
        """Alias for ``parse_html`` to satisfy the interface contract."""
        return self.parse_html(html)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _walk(
        self,
        node: Tag,
        elements: list[DOMElement],
        depth: int,
        parent_tag: Optional[str],
    ) -> None:
        """Recursively walk the DOM tree and collect elements."""
        tag_counts: Counter[str] = Counter()
        children = [c for c in node.children if isinstance(c, Tag)]

        for idx, child in enumerate(children):
            tag_name = child.name
            if tag_name in self._skip_tags:
                continue

            tag_counts[tag_name] += 1
            xpath = self._compute_xpath(child)

            raw_classes = child.get("class", [])
            classes = raw_classes if isinstance(raw_classes, list) else str(raw_classes).split()

            attrs: dict[str, str] = {}
            for k, v in child.attrs.items():
                if k == "class":
                    continue
                attrs[k] = v if isinstance(v, str) else " ".join(v)

            element_id = child.get("id")
            data_testid = child.get("data-testid")

            text = child.get_text(separator=" ", strip=True) or ""

            direct_children = [c for c in child.children if isinstance(c, Tag)]

            elem = DOMElement(
                tag=tag_name,
                element_id=element_id if isinstance(element_id, str) else None,
                classes=classes,
                text=text[:500],  # cap text length
                attributes=attrs,
                data_testid=data_testid if isinstance(data_testid, str) else None,
                depth=depth,
                child_index=idx,
                xpath=xpath,
                parent_tag=parent_tag,
                child_count=len(direct_children),
            )
            elements.append(elem)

            # Recurse into children
            self._walk(child, elements, depth=depth + 1, parent_tag=tag_name)

    @staticmethod
    def _compute_xpath(tag: Tag) -> str:
        """Build a simple XPath expression for the given tag."""
        parts: list[str] = []
        current: Tag | None = tag
        while current and isinstance(current, Tag) and current.name != "[document]":
            name = current.name
            siblings = [
                s for s in (current.parent.children if current.parent else [])
                if isinstance(s, Tag) and s.name == name
            ]
            if len(siblings) > 1:
                position = 1
                for s in siblings:
                    if s is current:
                        break
                    position += 1
                parts.append(f"{name}[{position}]")
            else:
                parts.append(name)
            current = current.parent  # type: ignore[assignment]
        parts.reverse()
        return "/" + "/".join(parts)
