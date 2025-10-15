"""Routes for the Signallisten tab."""
from __future__ import annotations

from quart import Blueprint, render_template

blueprint = Blueprint("signallisten", __name__)


@blueprint.get("/")
async def index() -> str:
    return await render_template("signallisten/index.html", active_tab="Signallisten", section="overview")


@blueprint.get("/import")
async def import_view() -> str:
    return await render_template("signallisten/import.html", active_tab="Signallisten", section="import")
