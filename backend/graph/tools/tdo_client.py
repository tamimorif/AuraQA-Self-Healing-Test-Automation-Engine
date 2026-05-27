"""
TDO (Test Data Orchestrator) client for AuraQA.

Provisions synthetic test data via the external TDO service.  When the
service is not configured the client returns deterministic placeholder
records so the pipeline can continue in local/dev environments.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx

from backend.config.settings import get_settings
from backend.models.schemas import TDORequest, TDOResponse

logger = logging.getLogger(__name__)


class TDOClient:
    """Async client for the Test Data Orchestrator service."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.tdo_base_url).rstrip("/")
        self.api_key = api_key or settings.tdo_api_key
        self._configured = bool(self.base_url and self.api_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def provision(self, request: TDORequest) -> TDOResponse:
        """
        Request synthetic test data from TDO.

        Returns:
            ``TDOResponse`` with provisioned records.  In dry-run mode
            placeholder records are generated locally.
        """
        if not self._configured:
            logger.warning("TDO not configured — returning placeholder data")
            return self._placeholder_response(request)

        return await self._post_provision(request)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _post_provision(self, request: TDORequest) -> TDOResponse:
        url = f"{self.base_url}/api/v1/provision"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=request.model_dump(), headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return TDOResponse(**data)

    @staticmethod
    def _placeholder_response(request: TDORequest) -> TDOResponse:
        """Generate deterministic placeholder records for dev/test use."""
        records: list[dict[str, Any]] = []
        for i in range(request.record_count):
            record: dict[str, Any] = {}
            for field_name, data_type in request.schema_fields.items():
                match data_type:
                    case "email":
                        record[field_name] = f"user{i}@example.com"
                    case "full_name" | "name":
                        record[field_name] = f"Test User {i}"
                    case "phone":
                        record[field_name] = f"+1-555-{1000 + i}"
                    case "integer" | "int":
                        record[field_name] = i
                    case "boolean" | "bool":
                        record[field_name] = i % 2 == 0
                    case "uuid":
                        record[field_name] = str(uuid.uuid4())
                    case _:
                        record[field_name] = f"{field_name}_value_{i}"
            records.append(record)

        return TDOResponse(
            request_id=str(uuid.uuid4()),
            test_case_id=request.test_case_id,
            dataset_name=request.dataset_name,
            records=records,
            record_count=len(records),
            provisioned_at=datetime.now(timezone.utc),
        )
