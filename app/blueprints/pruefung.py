"""Routes for the Prüfung tab."""
from __future__ import annotations

from quart import Blueprint, render_template

blueprint = Blueprint("pruefung", __name__)


@blueprint.get("/")
async def index() -> str:
    return await render_template("pruefung/index.html", active_tab="Prüfung", section="overview")


@blueprint.get("/verbindung")
async def verbindung() -> str:
    return await render_template("pruefung/verbindung.html", active_tab="Prüfung", section="verbindung")


@blueprint.get("/senden")
async def senden() -> str:
    return await render_template("pruefung/senden.html", active_tab="Prüfung", section="senden")


@blueprint.get("/monitor")
async def monitor() -> str:
    return await render_template("pruefung/monitor.html", active_tab="Prüfung", section="monitor")
