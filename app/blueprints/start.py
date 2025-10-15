from __future__ import annotations

from flask import Blueprint, current_app, render_template


bp = Blueprint("start", __name__)


@bp.get("/")
async def index() -> str:
    app = current_app
    render = app.ensure_async(render_template)
    return await render(
        "start/index.html",
        tab="Start",
        sidebar_items=[
            {"label": "Übersicht", "href": "#"},
            {"label": "Aktive Verbindungen", "href": "#connections"},
        ],
        client_metrics=app.iec_client.metrics,  # type: ignore[attr-defined]
        server_metrics=app.iec_server.metrics,  # type: ignore[attr-defined]
    )
