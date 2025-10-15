from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Deque, Dict, Iterable, List, Optional


@dataclass(slots=True)
class FramePayload:
    timestamp: datetime
    role: str
    direction: str
    apci_hex: str
    asdu_hex: str
    decoded: Dict[str, Any]


@dataclass(slots=True)
class FrameFilter:
    role: Optional[str] = None
    direction: Optional[str] = None
    ti: Optional[str] = None
    cot: Optional[str] = None
    ioa: Optional[str] = None
    text: Optional[str] = None

    def match(self, frame: FramePayload) -> bool:
        if self.role and frame.role != self.role:
            return False
        if self.direction and frame.direction != self.direction:
            return False
        decoded = frame.decoded
        if self.ti and str(decoded.get("ti")) != self.ti:
            return False
        if self.cot and str(decoded.get("cot")) != self.cot:
            return False
        if self.ioa:
            ioas = decoded.get("ioa", [])
            if not any(self.ioa in str(item) for item in ioas):
                return False
        if self.text:
            text_lower = self.text.lower()
            haystacks = [frame.apci_hex, frame.asdu_hex, repr(decoded)]
            if not any(text_lower in str(h).lower() for h in haystacks):
                return False
        return True


@dataclass
class Subscription:
    queue: "asyncio.Queue[FramePayload]"
    filters: FrameFilter = field(default_factory=FrameFilter)


class StreamBus:
    def __init__(self, history_limit: int = 10_000, queue_limit: int = 512) -> None:
        self._history_limit = history_limit
        self._queue_limit = queue_limit
        self._history: Deque[FramePayload] = deque(maxlen=history_limit)
        self._subscriptions: Dict[str, Subscription] = {}
        self._lock = asyncio.Lock()

    async def publish(self, key: str, frame: FramePayload) -> None:
        async with self._lock:
            self._history.append(frame)
            for sid, subscription in list(self._subscriptions.items()):
                queue = subscription.queue
                if queue.full():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                try:
                    queue.put_nowait(frame)
                except asyncio.QueueFull:
                    # Drop frame for this subscriber to ensure non-blocking behavior
                    continue

    async def history(self, limit: int, offset: int = 0) -> List[FramePayload]:
        async with self._lock:
            history_list = list(self._history)
        start = max(0, len(history_list) - offset - limit)
        end = len(history_list) - offset
        if end <= start:
            return []
        return history_list[start:end]

    async def subscribe(self, sid: str) -> Subscription:
        queue: "asyncio.Queue[FramePayload]" = asyncio.Queue(maxsize=self._queue_limit)
        subscription = Subscription(queue=queue)
        async with self._lock:
            self._subscriptions[sid] = subscription
        return subscription

    async def unsubscribe(self, sid: str) -> None:
        async with self._lock:
            subscription = self._subscriptions.pop(sid, None)
        if subscription:
            while not subscription.queue.empty():
                subscription.queue.get_nowait()

    async def update_filters(self, sid: str, **filters: Optional[str]) -> None:
        async with self._lock:
            subscription = self._subscriptions.get(sid)
            if not subscription:
                return
            for key, value in filters.items():
                if hasattr(subscription.filters, key):
                    setattr(subscription.filters, key, value or None)

    async def get_filtered_batch(
        self, sid: str, max_items: int, filters: Optional[FrameFilter] = None
    ) -> List[FramePayload]:
        async with self._lock:
            subscription = self._subscriptions.get(sid)
            if not subscription:
                return []
            filter_obj = filters or subscription.filters
        batch: List[FramePayload] = []
        queue = subscription.queue
        for _ in range(max_items):
            try:
                frame = queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            if filter_obj.match(frame):
                batch.append(frame)
        return batch

    async def list_subscribers(self) -> List[str]:
        async with self._lock:
            return list(self._subscriptions.keys())


__all__ = ["FramePayload", "StreamBus", "FrameFilter", "Subscription"]
