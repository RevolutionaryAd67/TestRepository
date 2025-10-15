from __future__ import annotations

import csv
import io
import json
from typing import Any

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from ..models.signale import SignalRepository
from ..utils.validation import validate_signal_rows


bp = Blueprint("signallisten", __name__)


@bp.get("/")
async def index() -> str:
    app = current_app
    render = app.ensure_async(render_template)
    repo = SignalRepository(app.db_session())  # type: ignore[attr-defined]
    signals = repo.list_signals()
    return await render(
        "signallisten/index.html",
        tab="Signallisten",
        sidebar_items=[
            {"label": "Import", "href": "#import"},
            {"label": "Export", "href": "#export"},
            {"label": "Mapping", "href": "#mapping"},
        ],
        signals=signals,
    )


@bp.post("/import")
async def import_records() -> Any:
    form = request.form
    payload = form.get("payload", "")
    fmt = form.get("format", "json")
    if not payload:
        flash("Keine Daten übergeben", "error")
        return redirect(url_for("signallisten.index"))

    if fmt == "json":
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            flash(f"JSON Fehler: {exc}", "error")
            return redirect(url_for("signallisten.index"))
    else:
        data = []
        reader = csv.DictReader(io.StringIO(payload))
        for row in reader:
            data.append(row)

    try:
        validated = validate_signal_rows(data)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("signallisten.index"))

    repo = SignalRepository(current_app.db_session())  # type: ignore[attr-defined]
    repo.import_records([row.model_dump() for row in validated])
    flash(f"{len(validated)} Signale importiert", "success")
    return redirect(url_for("signallisten.index"))


@bp.get("/export")
async def export_records() -> Response:
    fmt = request.args.get("format", "json")
    repo = SignalRepository(current_app.db_session())  # type: ignore[attr-defined]
    records = repo.export()
    if fmt == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=["name", "ti", "ioa", "scale", "unit", "default", "description"],
        )
        writer.writeheader()
        writer.writerows(records)
        csv_data = buffer.getvalue()
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=signale.csv"},
        )
    return Response(
        json.dumps(records, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=signale.json"},
    )
