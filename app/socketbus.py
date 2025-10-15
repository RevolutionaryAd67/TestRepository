"""Socket broadcast bus for IEC-104 frame events."""
from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, MutableSequence


@dataclass(slots=True)
class FrameEvent:
    ts: str
    role: str
    dir: str
    apci: str
    asdu: str
    decoded: Dict[str, Any]

    @classmethod
    def from_payload(
        cls, *, role: str, direction: str, apci: bytes, asdu: bytes, decoded: Dict[str, Any]
    ) -> "FrameEvent":
        timestamp = datetime.now(timezone.utc).isoformat()
        return cls(
            ts=timestamp,
            role=role,
            dir=direction,
            apci=apci.hex(),
            asdu=asdu.hex(),
            decoded=decoded,
        )


class FrameSocketBus:
    """In-memory fan-out for frame events with drop-oldest semantics."""

    def __init__(self, capacity: int) -> None:
        self._history: Deque[FrameEvent] = deque(maxlen=capacity)
        self._listeners: MutableSequence[asyncio.Queue[Dict[str, Any]]] = []

    def snapshot(self) -> List[Dict[str, Any]]:
        return [asdict(event) for event in list(self._history)]

    def register(self) -> asyncio.Queue[Dict[str, Any]]:
        queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=512)
        for event in self._history:
            queue.put_nowait(asdict(event))
        self._listeners.append(queue)
        return queue

    def unregister(self, queue: asyncio.Queue[Dict[str, Any]]) -> None:
        if queue in self._listeners:
            self._listeners.remove(queue)

    def publish(self, event: FrameEvent) -> None:
        self._history.append(event)
        payload = asdict(event)
        for queue in list(self._listeners):
            if queue.full():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:  # pragma: no cover - defensive
                    pass
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:  # pragma: no cover - defensive
                continue


__all__ = ["FrameEvent", "FrameSocketBus"]
