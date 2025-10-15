from __future__ import annotations

import json
from typing import Any, Dict

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from ..services.scenarios import DEFAULT_SCENARIOS


bp = Blueprint("pruefung", __name__)


def _parse_payload(form: Dict[str, str]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "ti": form.get("ti", ""),
        "cot": form.get("cot", ""),
        "ioa": form.get("ioa", ""),
    }
    values_raw = form.get("values", "")
    if values_raw:
        try:
            payload["values"] = json.loads(values_raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Ungültiges JSON in Values: {exc}") from exc
    return payload


@bp.get("/")
async def index() -> str:
    app = current_app
    render = app.ensure_async(render_template)
    return await render(
        "pruefung/index.html",
        tab="Prüfung",
        sidebar_items=[
            {"label": "Verbindungen", "href": "#connections"},
            {"label": "Sende-Vorlagen", "href": "#templates"},
            {"label": "Sequenzen", "href": "#scenarios"},
        ],
        client_metrics=app.iec_client.metrics,  # type: ignore[attr-defined]
        server_metrics=app.iec_server.metrics,  # type: ignore[attr-defined]
        scenarios=DEFAULT_SCENARIOS,
    )


@bp.post("/connect")
async def connect_client() -> Any:
    await current_app.iec_client.connect()  # type: ignore[attr-defined]
    flash("IEC-104 Client verbunden", "success")
    return redirect(url_for("pruefung.index"))


@bp.post("/disconnect")
async def disconnect_client() -> Any:
    await current_app.iec_client.disconnect()  # type: ignore[attr-defined]
    flash("IEC-104 Client getrennt", "info")
    return redirect(url_for("pruefung.index"))


@bp.post("/send")
async def send_asdu() -> Any:
    form = request.form.to_dict()
    try:
        payload = _parse_payload(form)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("pruefung.index"))
    await current_app.iec_client.send_asdu(payload)  # type: ignore[attr-defined]
    flash("ASDU gesendet", "success")
    return redirect(url_for("pruefung.index"))


@bp.post("/server/start")
async def start_server() -> Any:
    await current_app.iec_server.start()  # type: ignore[attr-defined]
    flash("IEC-104 Server gestartet", "success")
    return redirect(url_for("pruefung.index"))


@bp.post("/server/stop")
async def stop_server() -> Any:
    await current_app.iec_server.stop()  # type: ignore[attr-defined]
    flash("IEC-104 Server gestoppt", "info")
    return redirect(url_for("pruefung.index"))
