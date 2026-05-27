"""
LangGraph healing pipeline builder.

Constructs the ``StateGraph`` that implements the AuraQA self-healing
algorithm:

    analyze_dom → generate_selector → validate_selector
        → [conditional: rerun_test | generate_selector | escalate]
"""
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from backend.graph.edges.routing import route_after_validation
from backend.graph.nodes.analyze_dom import analyze_dom
from backend.graph.nodes.escalate import escalate
from backend.graph.nodes.generate_selector import generate_selector
from backend.graph.nodes.provision_test_data import provision_test_data
from backend.graph.nodes.rerun_test import rerun_test
from backend.graph.nodes.validate_selector import validate_selector
from backend.graph.state import HealingState

logger = logging.getLogger(__name__)


def build_healing_graph() -> StateGraph:
    """
    Build and compile the self-healing LangGraph pipeline.

    Graph topology::

        START
          │
          ▼
        analyze_dom
          │
          ▼
        generate_selector
          │
          ▼
        validate_selector
          │
          ├─ confidence ≥ 80% ──► provision_test_data ──► rerun_test ──► END
          │
          ├─ attempts < max ────► generate_selector  (retry loop)
          │
          └─ else ──────────────► escalate ──► END

    Returns:
        A compiled ``StateGraph`` ready for ``.invoke(state)``.
    """
    graph = StateGraph(HealingState)

    # ---- Register nodes ----
    graph.add_node("analyze_dom", analyze_dom)
    graph.add_node("generate_selector", generate_selector)
    graph.add_node("validate_selector", validate_selector)
    graph.add_node("provision_test_data", provision_test_data)
    graph.add_node("rerun_test", rerun_test)
    graph.add_node("escalate", escalate)

    # ---- Static edges ----
    graph.set_entry_point("analyze_dom")
    graph.add_edge("analyze_dom", "generate_selector")
    graph.add_edge("generate_selector", "validate_selector")

    # ---- Conditional edge after validation ----
    graph.add_conditional_edges(
        "validate_selector",
        route_after_validation,
        {
            "rerun_test": "provision_test_data",
            "generate_selector": "generate_selector",
            "escalate": "escalate",
        },
    )

    # ---- Terminal edges ----
    graph.add_edge("provision_test_data", "rerun_test")
    graph.add_edge("rerun_test", END)
    graph.add_edge("escalate", END)

    compiled = graph.compile()
    logger.info("Healing graph compiled successfully")
    return compiled
