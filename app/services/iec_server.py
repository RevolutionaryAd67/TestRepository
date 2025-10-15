"""Wrapper around the iec104.IEC104Server class."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

from iec104 import IEC104Server, decode_asdu

from ..socketbus import FrameEvent, FrameSocketBus
from .iec_client import _serialize_asdu

logger = logging.getLogger(__name__)

IncomingHandler = Callable[[Any], Awaitable[None]]


@dataclass(slots=True)
class IEC104ServerConfig:
    host: str = "0.0.0.0"
    port: int = 2404
    k: int = 12
    w: int = 8
    t0: float = 30.0
    t1: float = 15.0
    t2: float = 10.0
    t3: float = 20.0


class IEC104ServerService:
    """Async wrapper for the IEC104Server."""

    def __init__(self, bus: FrameSocketBus, config: Optional[IEC104ServerConfig] = None) -> None:
        self._bus = bus
        self._config = config or IEC104ServerConfig()
        self._server: Optional[IEC104Server] = None
        self._task: Optional[asyncio.Task[None]] = None
        self._handlers: Dict[int, IncomingHandler] = {}
        self._stats: Dict[str, int] = {"rx": 0, "tx": 0}

    @property
    def stats(self) -> Dict[str, int]:
        return dict(self._stats)

    def register_handler(self, ti: int, handler: IncomingHandler) -> None:
        self._handlers[ti] = handler

    async def start(self) -> None:
        if self._server is not None:
            return
        self._server = IEC104Server(
            host=self._config.host,
            port=self._config.port,
            k=self._config.k,
            w=self._config.w,
            t0=self._config.t0,
            t1=self._config.t1,
            t2=self._config.t2,
            t3=self._config.t3,
        )
        start_fn = getattr(self._server, 'start', None)
        if start_fn is None:
            raise RuntimeError('IEC104Server missing start method')
        await asyncio.to_thread(start_fn)
        self._task = asyncio.create_task(self._serve_loop())
        logger.info("IEC104 server listening", extra={"host": self._config.host, "port": self._config.port})

    async def stop(self) -> None:
        if self._server is None:
            return
        server = self._server
        self._server = None
        if self._task:
            self._task.cancel()
        stop_fn = getattr(server, 'stop', None)
        if stop_fn is not None:
            await asyncio.to_thread(stop_fn)
        logger.info("IEC104 server stopped")

    async def send_asdu(self, payload: bytes) -> None:
        if self._server is None:
            raise RuntimeError("IEC104 server not running")
        broadcast_fn = getattr(self._server, 'broadcast', None)
        if broadcast_fn is None:
            raise RuntimeError('IEC104Server missing broadcast method')
        await asyncio.to_thread(broadcast_fn, payload)
        self._stats["tx"] += 1
        self._bus.publish(
            FrameEvent.from_payload(
                role="server",
                direction="tx",
                apci=payload[:4],
                asdu=payload[4:],
                decoded={},
            )
        )

    async def _serve_loop(self) -> None:
        assert self._server is not None
        server = self._server
        while True:
            try:
                accept_fn = getattr(server, 'accept', None)
                if accept_fn is None:
                    await asyncio.sleep(1)
                    continue
                connection = await asyncio.to_thread(accept_fn)
            except asyncio.CancelledError:  # pragma: no cover - shutdown
                raise
            except Exception as exc:  # pragma: no cover - network errors
                logger.exception("IEC104 server accept loop error: %s", exc)
                await asyncio.sleep(1)
                continue
            asyncio.create_task(self._connection_loop(connection))

    async def _connection_loop(self, connection: Any) -> None:
        logger.info("IEC104 server accepted connection", extra={"peer": getattr(connection, "peer", "unknown")})
        start_dt = getattr(connection, "start_dt", None)
        if callable(start_dt):
            await asyncio.to_thread(start_dt)
        while True:
            try:
                receive_fn = getattr(connection, 'receive', None)
                if receive_fn is None:
                    await asyncio.sleep(1)
                    continue
                message = await asyncio.to_thread(receive_fn)
            except asyncio.CancelledError:  # pragma: no cover - shutdown
                raise
            except Exception as exc:  # pragma: no cover - network errors
                logger.exception("IEC104 server connection loop error: %s", exc)
                break
            apci_bytes = getattr(message, "apci", b"") if message is not None else b""
            asdu_bytes = getattr(message, "asdu", b"") if message is not None else b""
            decoded: Dict[str, Any] = {}
            if isinstance(asdu_bytes, (bytes, bytearray)) and asdu_bytes:
                try:
                    decoded_obj = decode_asdu(asdu_bytes)
                    decoded = _serialize_asdu(decoded_obj)
                except Exception:  # pragma: no cover
                    decoded = {"error": "decode_failed"}
            self._stats["rx"] += 1
            self._bus.publish(
                FrameEvent.from_payload(
                    role="server",
                    direction="rx",
                    apci=bytes(apci_bytes) if isinstance(apci_bytes, (bytes, bytearray)) else b"",
                    asdu=bytes(asdu_bytes) if isinstance(asdu_bytes, (bytes, bytearray)) else b"",
                    decoded=decoded,
                )
            )
            ti = decoded.get("ti") if isinstance(decoded, dict) else None
            if isinstance(ti, int) and ti in self._handlers:
                await self._handlers[ti](decoded)

__all__ = ['IEC104ServerService', 'IEC104ServerConfig']
