from __future__ import annotations

import asyncio
from typing import Any

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .config import Settings, load_settings
from .models.signale import Base
from .services.iec_client import ClientConfiguration, IEC104ClientService
from .services.iec_server import IEC104ServerService, ServerConfiguration
from .socketio import configure_socketio


def create_app(settings: Settings | None = None) -> Flask:
    loader = load_settings() if settings is None else None
    settings_obj = settings or (loader.settings if loader else Settings())

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.update(SECRET_KEY=settings_obj.secret_key)
    app.settings = settings_obj  # type: ignore[attr-defined]

    engine = create_engine(settings_obj.database.url, echo=settings_obj.database.echo, future=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    app.db_session = scoped_session(session_factory)  # type: ignore[attr-defined]

    Base.metadata.create_all(engine)

    client_config = ClientConfiguration(
        host=settings_obj.iec.host,
        port=settings_obj.iec.port,
        k_window=settings_obj.iec.k_window,
        w_window=settings_obj.iec.w_window,
        t0=settings_obj.iec.t0,
        t1=settings_obj.iec.t1,
        t2=settings_obj.iec.t2,
        t3=settings_obj.iec.t3,
    )
    server_config = ServerConfiguration(host=settings_obj.iec.server_host, port=settings_obj.iec.server_port)
    app.iec_client = IEC104ClientService(client_config)  # type: ignore[attr-defined]
    app.iec_server = IEC104ServerService(server_config)  # type: ignore[attr-defined]

    register_blueprints(app)
    configure_socketio(app)

    @app.context_processor
    def inject_defaults() -> dict[str, object]:
        from datetime import datetime

        return {
            "current_year": datetime.utcnow().year,
            "client_metrics": app.iec_client.metrics,  # type: ignore[attr-defined]
            "server_metrics": app.iec_server.metrics,  # type: ignore[attr-defined]
        }

    @app.teardown_appcontext
    def remove_session(_: Any) -> None:
        if hasattr(app, "db_session"):
            app.db_session.remove()  # type: ignore[attr-defined]

    return app


def register_blueprints(app: Flask) -> None:
    from .blueprints import admin, pruefung, signallisten, start

    app.register_blueprint(start.bp)
    app.register_blueprint(pruefung.bp, url_prefix="/pruefung")
    app.register_blueprint(signallisten.bp, url_prefix="/signallisten")
    app.register_blueprint(admin.bp, url_prefix="/admin")


async def run_app(app: Flask) -> None:
    from .socketio import socketio

    await socketio.run_async(app, host="0.0.0.0", port=app.settings.iec.server_port)  # type: ignore[attr-defined]


def main() -> None:
    app = create_app()
    asyncio.run(run_app(app))


if __name__ == "__main__":
    main()
