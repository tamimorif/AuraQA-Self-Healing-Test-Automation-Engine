"""
AuraQA Environment Variable Schema.

Pydantic Settings model validating all required and optional env vars.
Loaded from .env file or system environment at startup.
"""
from __future__ import annotations

from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class AuraQASettings(BaseSettings):
    """Validated environment configuration for AuraQA."""

    # --- Application ---
    app_name: str = Field("AuraQA", description="Application name")
    app_version: str = Field("1.0.0", description="Application version")
    app_env: str = Field("development", description="Environment: development|staging|production")
    debug: bool = Field(False, description="Enable debug mode")
    log_level: str = Field("INFO", description="Logging level")

    # --- API Server ---
    api_host: str = Field("0.0.0.0", description="API bind host")
    api_port: int = Field(8000, ge=1, le=65535, description="API bind port")
    api_workers: int = Field(1, ge=1, le=16, description="Uvicorn worker count")
    cors_origins: str = Field(
        "http://localhost:5173,http://localhost:3000",
        description="Comma-separated CORS allowed origins",
    )

    # --- LangGraph ---
    langgraph_max_retries: int = Field(3, ge=1, le=10, description="Max healing retry attempts")
    confidence_threshold: float = Field(
        80.0, ge=0.0, le=100.0, description="Min confidence to accept healed selector"
    )

    # --- Jira Integration ---
    jira_base_url: str = Field("", description="Jira instance base URL")
    jira_project_key: str = Field("AURA", description="Jira project key for audit issues")
    jira_api_token: str = Field("", description="Jira API authentication token")
    jira_user_email: str = Field("", description="Jira user email for API auth")
    jira_issue_type: str = Field("Bug", description="Default Jira issue type")

    # --- UiPath ---
    uipath_orchestrator_url: str = Field("", description="UiPath Orchestrator base URL")
    uipath_tenant: str = Field("", description="UiPath tenant name")
    uipath_api_key: str = Field("", description="UiPath API key")
    uipath_folder_id: str = Field("", description="UiPath folder/organization ID")

    # --- TDO (Test Data Orchestrator) ---
    tdo_base_url: str = Field("", description="TDO service base URL")
    tdo_api_key: str = Field("", description="TDO API authentication key")
    tdo_default_dataset: str = Field("default", description="Default TDO dataset name")

    # --- Mock App ---
    mock_app_url: str = Field(
        "http://localhost:5173", description="Mock React app URL for testing"
    )

    @field_validator("app_env", mode="before")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}, got '{v}'")
        return v

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}, got '{v}'")
        return upper

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_prefix": "AURAQA_",
        "case_sensitive": False,
    }
