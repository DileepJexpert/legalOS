from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.db.session import SessionLocal, create_all_tables

logger = logging.getLogger("legalos.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every incoming request and its response status + duration."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        start = time.perf_counter()
        # Log request arrival
        logger.info(
            "→ %s %s  client=%s",
            request.method,
            request.url.path,
            getattr(request.client, "host", "unknown"),
        )
        try:
            response = await call_next(request)
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            logger.exception(
                "✗ %s %s  UNHANDLED EXCEPTION  %.1fms",
                request.method,
                request.url.path,
                elapsed,
            )
            raise
        elapsed = (time.perf_counter() - start) * 1000
        level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            level,
            "← %s %s  [%s]  %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
        )
        return response


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    setup_logging(debug=settings.app_debug)
    startup_log = logging.getLogger("legalos.startup")
    startup_log.info("=== LegalOS API starting up ===")
    startup_log.info("env=%s  bypass_auth=%s  db=%s",
                     settings.app_env,
                     settings.bypass_auth,
                     settings.database_url.split("@")[-1] if "@" in settings.database_url
                     else settings.database_url)
    if settings.auto_create_db:
        startup_log.info("AUTO_CREATE_DB=true — creating tables")
        await create_all_tables()
    startup_log.info("=== startup complete — listening ===")
    yield
    logging.getLogger("legalos.startup").info("=== LegalOS API shutting down ===")


def build_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # In development, accept any localhost/127.0.0.1 port so that the frontend
    # can run on any dev-server port without CORS errors.
    if settings.app_env.lower() in {"development", "dev"}:
        app.add_middleware(
            CORSMiddleware,
            allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=settings.cors_methods,
            allow_headers=settings.cors_headers,
        )

    # Request logging must be added AFTER CORS so it wraps everything
    app.add_middleware(RequestLoggingMiddleware)

    app.state.session_factory = SessionLocal
    app.include_router(api_router, prefix="/api/v1")
    return app


app = build_application()
