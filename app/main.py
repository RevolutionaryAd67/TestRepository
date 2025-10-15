"""ASGI entry point for Hypercorn."""
from __future__ import annotations

import logging
import sys
from typing import Any

from quart import jsonify, websocket

from . import create_app

try:
    import iec104
except ImportError as exc:  # pragma: no cover - fail-fast during startup
    print(
        "[IEC104] Required package 'iec104' is missing. Install it with "
        "'pip install -e ../iec104' and ensure VS Code uses the correct "
        "Python interpreter.",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc

for symbol in (
    "IEC104Client",
    "IEC104Server",
    "encode_asdu",
    "decode_asdu",
    "M_SP_NA_1",
    "M_SP_TB_1",
    "M_ME_NC_1",
    "C_SC_NA_1",
):
    if not hasattr(iec104, symbol):  # pragma: no cover - validation logic
        print(
            f"[IEC104] Missing symbol '{symbol}' in package. Verify the package "
            "installation.",
            file=sys.stderr,
        )
        raise SystemExit(2)

app = create_app()
logger = logging.getLogger(__name__)


@app.get("/healthz")
async def healthcheck() -> Any:
    """Simple health check endpoint."""
    return jsonify({"status": "ok"})


@app.websocket("/stream")
async def stream() -> None:
    """Stream live IEC-104 frames to the browser via WebSocket."""
    queue = app.frame_bus.register()
    logger.debug("WebSocket client connected", extra={"route": "/stream"})
    try:
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except Exception:  # pragma: no cover - websocket transport errors
        logger.exception("WebSocket connection terminated unexpectedly")
    finally:
        app.frame_bus.unregister(queue)
        logger.debug("WebSocket client disconnected", extra={"route": "/stream"})


__all__ = ["app"]
