from __future__ import annotations

import asyncio
from typing import Any, Dict

from flask import Flask
from flask_socketio import Namespace, SocketIO

from .services.stream_bus import FramePayload, StreamBus


socketio = SocketIO(async_mode="asgi", transports=["websocket"], cors_allowed_origins="*")
stream_bus = StreamBus()


class StreamNamespace(Namespace):
    def __init__(self, namespace: str = "/stream") -> None:
        super().__init__(namespace)
        self._tasks: Dict[str, asyncio.Task[Any]] = {}

    async def on_connect(self, sid: str, environ: Dict[str, Any]) -> None:
        await stream_bus.subscribe(sid)
        await self._start_pump(sid)
        await self.emit("status", {"connected": True}, room=sid)

    async def on_disconnect(self, sid: str) -> None:
        await stream_bus.unsubscribe(sid)
        task = self._tasks.pop(sid, None)
        if task:
            task.cancel()

    async def on_filters(self, sid: str, data: Dict[str, Any]) -> None:
        await stream_bus.update_filters(
            sid,
            role=data.get("role"),
            direction=data.get("direction"),
            ti=data.get("ti"),
            cot=data.get("cot"),
            ioa=data.get("ioa"),
            text=data.get("text"),
        )

    async def on_history(self, sid: str, data: Dict[str, Any]) -> None:
        limit = int(data.get("limit", 200))
        offset = int(data.get("offset", 0))
        history = await stream_bus.history(limit=limit, offset=offset)
        await self.emit("history", [self._serialize(frame) for frame in history], room=sid)

    async def _start_pump(self, sid: str) -> None:
        loop = asyncio.get_running_loop()
        rate_limit = max(1, int(socketio.server_options.get("max_client_rate_fps", 30)))
        interval = 1.0 / float(rate_limit)

        async def pump() -> None:
            try:
                while True:
                    batch = await stream_bus.get_filtered_batch(sid, max_items=100)
                    if batch:
                        await self.emit("frames", [self._serialize(f) for f in batch], room=sid)
                    await asyncio.sleep(interval)
            except asyncio.CancelledError:
                return

        task = loop.create_task(pump())
        self._tasks[sid] = task

    @staticmethod
    def _serialize(frame: FramePayload) -> Dict[str, Any]:
        return {
            "timestamp": frame.timestamp.isoformat(),
            "role": frame.role,
            "direction": frame.direction,
            "apci_hex": frame.apci_hex,
            "asdu_hex": frame.asdu_hex,
            "decoded": frame.decoded,
        }


def configure_socketio(app: Flask) -> None:
    socketio.server_options["max_client_rate_fps"] = app.settings.stream.max_client_rate_fps  # type: ignore[attr-defined]
    socketio.init_app(app, transports=["websocket"], async_mode="asgi")
    socketio.on_namespace(StreamNamespace("/stream"))


async def emit_frame(payload: FramePayload) -> None:
    await stream_bus.publish("stream", payload)


__all__ = ["socketio", "configure_socketio", "emit_frame", "stream_bus"]
