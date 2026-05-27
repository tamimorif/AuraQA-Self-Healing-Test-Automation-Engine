"""
AuraQA Runtime Configuration Loader.

Singleton settings instance used across the application.
"""
from __future__ import annotations

import logging
from functools import lru_cache

from backend.config.env_schema import AuraQASettings


@lru_cache(maxsize=1)
def get_settings() -> AuraQASettings:
    """
    Load and cache application settings.

    Returns:
        AuraQASettings: Validated settings instance.

    Raises:
        pydantic.ValidationError: If required env vars are missing or invalid.
    """
    return AuraQASettings()


def configure_logging(settings: AuraQASettings) -> None:
    """
    Configure application logging based on settings.

    Args:
        settings: Validated application settings.
    """
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
