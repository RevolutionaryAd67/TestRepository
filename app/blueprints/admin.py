"""Routes for the Administration tab."""
from __future__ import annotations

from quart import Blueprint, current_app, render_template

blueprint = Blueprint("admin", __name__)


@blueprint.get("/")
async def index() -> str:
    settings = current_app.config["settings"]
    return await render_template("admin.html", active_tab="Administration", section="overview", settings=settings)
