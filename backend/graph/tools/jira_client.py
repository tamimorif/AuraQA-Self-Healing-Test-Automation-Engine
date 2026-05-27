"""
Jira REST API client for AuraQA audit issue creation.

Creates Bug / escalation issues in Jira when the self-healing pipeline
cannot confidently heal a broken selector.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from backend.config.settings import get_settings
from backend.models.schemas import AuditLogEntry, JiraPriority

logger = logging.getLogger(__name__)


class JiraClient:
    """
    Thin wrapper around the Jira REST API v2 for issue creation.

    When Jira credentials are not configured the client operates in
    *dry-run* mode — it logs the payload and returns a synthetic key.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_token: str | None = None,
        user_email: str | None = None,
        project_key: str | None = None,
        issue_type: str | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.jira_base_url).rstrip("/")
        self.api_token = api_token or settings.jira_api_token
        self.user_email = user_email or settings.jira_user_email
        self.project_key = project_key or settings.jira_project_key
        self.issue_type = issue_type or settings.jira_issue_type
        self._configured = bool(self.base_url and self.api_token and self.user_email)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def create_issue(
        self,
        audit: AuditLogEntry,
        *,
        priority: JiraPriority | None = None,
    ) -> str:
        """
        Create a Jira issue from an audit log entry.

        Returns:
            The Jira issue key (e.g. ``AURA-42``) or a synthetic key in
            dry-run mode.
        """
        effective_priority = priority or audit.jira_priority
        summary = (
            f"[AuraQA] Selector drift detected — "
            f"{audit.test_case_id} ({audit.drift_type or 'unknown'})"
        )
        description = self._build_description(audit)
        payload = self._build_payload(summary, description, effective_priority)

        if not self._configured:
            logger.warning(
                "Jira not configured — dry-run issue: %s | priority=%s",
                summary,
                effective_priority.value,
            )
            return f"{self.project_key}-DRY-{audit.audit_id[:8]}"

        return await self._post_issue(payload)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _build_payload(
        self,
        summary: str,
        description: str,
        priority: JiraPriority,
    ) -> dict[str, Any]:
        return {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": self.issue_type},
                "priority": {"name": priority.value},
                "labels": ["auraqa", "self-healing", "selector-drift"],
            }
        }

    @staticmethod
    def _build_description(audit: AuditLogEntry) -> str:
        lines = [
            f"*Test Case*: {audit.test_case_id}",
            f"*Test Suite*: {audit.test_suite_id}",
            f"*Page URL*: {audit.page_url}",
            f"*Environment*: {audit.environment}",
            f"*Broken Selector*: {{code}}{audit.original_selector}{{code}}",
            f"*Healed Selector*: {{code}}{audit.healed_selector or 'N/A'}{{code}}",
            f"*Confidence*: {audit.confidence:.1f}%",
            f"*Drift Type*: {audit.drift_type or 'undetected'}",
            f"*Status*: {audit.status.value}",
            f"*Attempts*: {audit.attempt_count}",
            f"*Execution Time*: {audit.execution_time_ms:.0f} ms",
            f"*Error*: {audit.error_message or 'N/A'}",
            "",
            "*Scoring Breakdown*:",
        ]
        for k, v in audit.scoring_breakdown.items():
            lines.append(f"  - {k}: {v:.4f}")
        return "\n".join(lines)

    async def _post_issue(self, payload: dict[str, Any]) -> str:
        url = f"{self.base_url}/rest/api/2/issue"
        headers = {"Content-Type": "application/json"}
        auth = (self.user_email, self.api_token)

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, auth=auth, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            key = data.get("key", "UNKNOWN")
            logger.info("Created Jira issue %s", key)
            return key
