"""Async pub/sub bus for live IEC-104 events."""

from __future__ import annotations

import asyncio
from collections import deque
from typing import AsyncIterator, Deque

from ..domain.events import IEC104FrameEvent

_MAX_QUEUE = 100


class LiveBus:
    """A lightweight broadcast bus backed by asyncio queues."""

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[IEC104FrameEvent]] = set()
        self._lock = asyncio.Lock()
        self._closed = False

    async def subscribe(self) -> AsyncIterator[IEC104FrameEvent]:
        queue: asyncio.Queue[IEC104FrameEvent] = asyncio.Queue(maxsize=_MAX_QUEUE)
        async with self._lock:
            if self._closed:
                raise RuntimeError("LiveBus is closed")
            self._subscribers.add(queue)

        try:
            while True:
                yield await queue.get()
        finally:
            async with self._lock:
                self._subscribers.discard(queue)

    async def publish(self, event: IEC104FrameEvent) -> None:
        async with self._lock:
            subscribers = list(self._subscribers)
        for queue in subscribers:
            if queue.full():
                drained: Deque[IEC104FrameEvent] = deque(maxlen=1)
                while not queue.empty():
                    drained.append(queue.get_nowait())
            queue.put_nowait(event)

    async def close(self) -> None:
        async with self._lock:
            self._closed = True
            self._subscribers.clear()


__all__ = ["LiveBus"]
