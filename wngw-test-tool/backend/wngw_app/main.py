"""FastAPI application entrypoint."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import routes_admin, routes_signal_lists, routes_tests, ws_live
from .config import get_settings
from .services.livebus import LiveBus

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown."""

    live_bus = LiveBus()
    app.state.live_bus = live_bus
    tasks: set[asyncio.Task[None]] = set()

    try:
        yield
    finally:
        logger.info("shutting down", extra={"component": "lifespan"})
        for task in tasks:
            task.cancel()
        await live_bus.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routes_admin.router, prefix=f"{settings.api_prefix}/admin")
    app.include_router(routes_tests.router, prefix=f"{settings.api_prefix}/tests")
    app.include_router(
        routes_signal_lists.router,
        prefix=f"{settings.api_prefix}/signal-lists",
    )
    app.include_router(ws_live.router)

    return app


app = create_app()
