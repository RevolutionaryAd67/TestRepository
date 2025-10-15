"""Project-internal contract for IEC-104 interactions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, Protocol

from ...domain.events import IEC104FrameEvent


@dataclass(slots=True)
class SingleCommandRequest:
    host: str
    port: int
    ca: int
    ioa: int
    value: bool


class IEC104ClientAdapter(Protocol):
    async def connect(self, host: str, port: int) -> None: ...

    async def close(self) -> None: ...

    async def send_single_command(self, ca: int, ioa: int, value: bool) -> None: ...

    async def recv_once(self, timeout: float | None = None) -> object | None: ...

    def on_rx(self, callback: Callable[[IEC104FrameEvent], Awaitable[None]]) -> None: ...


class IEC104ServerAdapter(Protocol):
    async def start(self, bind_ip: str, port: int) -> None: ...

    async def stop(self) -> None: ...

    def set_handler(
        self,
        handler: Callable[[object, object], Awaitable[None]],
    ) -> None: ...


class LiveEventPublisher(Protocol):
    async def publish(self, event: IEC104FrameEvent) -> None: ...


__all__ = [
    "SingleCommandRequest",
    "IEC104ClientAdapter",
    "IEC104ServerAdapter",
    "LiveEventPublisher",
]
