"""
AuraQA FastAPI application.

Exposes the self-healing REST API consumed by UiPath Orchestrator.

Endpoints:
    POST /heal          — Accept a test-failure payload and return a healed selector.
    GET  /health        — Liveness / readiness probe.
    GET  /              — Root welcome message.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config.settings import configure_logging, get_settings
from backend.models.schemas import (
    HealedSelectorResponse,
    HealingStatus,
    TestFailurePayload,
)
from backend.services.healing_service import HealingService

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Lifespan — startup / shutdown hooks
# ------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context: configure logging on startup."""
    settings = get_settings()
    configure_logging(settings)
    logger.info(
        "AuraQA %s starting (env=%s, debug=%s)",
        settings.app_version,
        settings.app_env,
        settings.debug,
    )
    yield
    logger.info("AuraQA shutting down")


# ------------------------------------------------------------------
# Application factory
# ------------------------------------------------------------------

def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Self-Healing Enterprise Test Automation Engine",
        lifespan=lifespan,
    )

    # ---- CORS ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Exception handler ----
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)},
        )

    # ---- Routes ----
    _register_routes(app)

    return app


# ------------------------------------------------------------------
# Route registration
# ------------------------------------------------------------------

def _register_routes(app: FastAPI) -> None:
    """Register all API routes on the application."""

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        """Root endpoint — welcome message."""
        settings = get_settings()
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "operational",
        }

    @app.get("/health", tags=["meta"])
    async def health_check() -> dict[str, str]:
        """Liveness / readiness probe."""
        return {"status": "healthy"}

    @app.post(
        "/heal",
        response_model=HealedSelectorResponse,
        tags=["healing"],
        summary="Heal a broken test selector",
        description=(
            "Accepts a test-failure payload from UiPath and returns a healed "
            "selector with confidence scoring and audit metadata."
        ),
    )
    async def heal_selector(payload: TestFailurePayload) -> HealedSelectorResponse:
        """
        Run the self-healing pipeline.

        Receives a ``TestFailurePayload`` from UiPath, executes the
        LangGraph healing graph, and returns a ``HealedSelectorResponse``.
        """
        logger.info(
            "POST /heal — test_case=%s broken_selector=%s",
            payload.test_case_id,
            payload.broken_selector,
        )
        try:
            service = HealingService()
            response = await service.heal(payload)
            return response
        except Exception as exc:
            logger.exception("Healing pipeline failed: %s", exc)
            raise HTTPException(
                status_code=500,
                detail=f"Healing pipeline error: {exc}",
            ) from exc


# ------------------------------------------------------------------
# Module-level app instance (for ``uvicorn backend.main:app``)
# ------------------------------------------------------------------

app = create_app()
