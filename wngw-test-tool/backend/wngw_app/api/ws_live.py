"""WebSocket endpoint for live IEC-104 events."""

from __future__ import annotations

import json

from ..domain.events import IEC104FrameEvent


class Router:
    def websocket(self, *_args, **_kwargs):  # pragma: no cover - placeholder
        return lambda func: func


router = Router()


def serialize_event(event: IEC104FrameEvent) -> str:
    return json.dumps(event.to_dict())


@router.websocket("/ws/live")
def websocket_live(websocket) -> None:  # pragma: no cover - placeholder
    raise NotImplementedError("WebSocket requires FastAPI runtime")


__all__ = ["router", "serialize_event"]
