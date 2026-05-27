"""
LangGraph node: provision synthetic test data via TDO.

Invokes the Test Data Orchestrator to provision any required data records
for the healed test case before re-execution.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from backend.graph.state import HealingState
from backend.graph.tools.tdo_client import TDOClient
from backend.models.schemas import TDORequest

logger = logging.getLogger(__name__)


def provision_test_data(state: HealingState) -> HealingState:
    """
    Provision synthetic test data from TDO.

    This node runs TDO provisioning synchronously by entering an
    event loop when called from a synchronous LangGraph pipeline.

    Updates:
        - ``tdo_data`` — provisioned records and metadata
    """
    logger.info("provision_test_data — requesting data from TDO")

    failure = state.get("failure_payload", {})
    test_case_id = failure.get("test_case_id", "unknown")
    environment = failure.get("environment", "staging")

    request = TDORequest(
        test_case_id=test_case_id,
        dataset_name="auto_heal",
        record_count=1,
        schema_fields={
            "email": "email",
            "name": "full_name",
        },
        environment=environment,
    )

    client = TDOClient()
    try:
        loop = _get_or_create_event_loop()
        response = loop.run_until_complete(client.provision(request))
        state["tdo_data"] = response.model_dump(mode="json")
        logger.info(
            "provision_test_data — provisioned %d record(s)",
            response.record_count,
        )
    except Exception as exc:
        logger.warning("provision_test_data — TDO error (non-fatal): %s", exc)
        state["tdo_data"] = {"error": str(exc)}

    return state


def _get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """Get the running event loop or create a new one."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("closed")
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
