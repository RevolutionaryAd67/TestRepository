"""Quart application factory for the IEC 60870-5-104 test environment."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from quart import Quart

from .config import AppSettings
from .models.signale import init_db
from .socketbus import FrameSocketBus


def create_app() -> Quart:
    """Create and configure the Quart application."""
    load_dotenv()
    settings = AppSettings()  # type: ignore[arg-type]

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s %(message)s",
    )

    app = Quart(__name__, static_folder=str(Path(__file__).parent / "static"))
    app.config["settings"] = settings

    app.frame_bus = FrameSocketBus(settings.stream_ringbuffer_capacity)

    @app.before_serving
    async def _startup() -> None:
        await init_db(settings.database_url)

    register_blueprints(app)

    @app.context_processor
    def _inject_settings():
        return {'config': {'settings': settings}}

    return app


def register_blueprints(app: Quart) -> None:
    """Import and register all blueprints."""
    from .blueprints import admin, pruefung, signallisten, start

    app.register_blueprint(start.blueprint)
    app.register_blueprint(pruefung.blueprint, url_prefix="/pruefung")
    app.register_blueprint(signallisten.blueprint, url_prefix="/signallisten")
    app.register_blueprint(admin.blueprint, url_prefix="/admin")


__all__ = ["create_app"]
