"""Routes for the Start tab."""
from __future__ import annotations

from quart import Blueprint, render_template

blueprint = Blueprint("start", __name__)


@blueprint.get("/")
async def index() -> str:
    return await render_template("start.html", active_tab="Start", section="overview")
