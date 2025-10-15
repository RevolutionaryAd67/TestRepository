from __future__ import annotations

import json
from typing import Any

from flask import Blueprint, Response, current_app, flash, redirect, render_template, request, url_for

from ..socketio import stream_bus


bp = Blueprint("admin", __name__)


@bp.get("/")
async def index() -> str:
    app = current_app
    render = app.ensure_async(render_template)
    settings = app.settings  # type: ignore[attr-defined]
    return await render(
        "admin/index.html",
        tab="Administration",
        sidebar_items=[
            {"label": "Allgemein", "href": "#general"},
            {"label": "WebSocket", "href": "#ws"},
            {"label": "Benutzer", "href": "#users"},
        ],
        settings=settings,
    )


@bp.post("/settings")
async def update_settings() -> Any:
    form = request.form
    app = current_app
    settings = app.settings  # type: ignore[attr-defined]
    log_level = form.get("log_level", settings.log_level)
    settings.log_level = log_level
    ringbuffer_size = form.get("ringbuffer_size")
    if ringbuffer_size:
        try:
            new_size = int(ringbuffer_size)
            app.settings.stream.ringbuffer_size = new_size  # type: ignore[attr-defined]
        except ValueError:
            flash("Ungültige Ringpuffergröße", "error")
            return redirect(url_for("admin.index"))
    flash("Einstellungen aktualisiert", "success")
    return redirect(url_for("admin.index"))


@bp.get("/ws-diagnostics")
async def ws_diagnostics() -> Response:
    subscribers = await stream_bus.list_subscribers()
    payload = {"subscribers": subscribers}
    return Response(json.dumps(payload), mimetype="application/json")
