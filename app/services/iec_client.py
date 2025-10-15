"""Wrapper around the iec104.IEC104Client class."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Dict, Optional

from iec104 import IEC104Client, decode_asdu, encode_asdu

from ..socketbus import FrameEvent, FrameSocketBus

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class IEC104ClientConfig:
    host: str = "127.0.0.1"
    port: int = 2404
    k: int = 12
    w: int = 8
    t0: float = 30.0
    t1: float = 15.0
    t2: float = 10.0
    t3: float = 20.0


class IEC104ClientService:
    """Asynchronous wrapper for IEC104Client with publish hooks."""

    def __init__(self, bus: FrameSocketBus, config: Optional[IEC104ClientConfig] = None) -> None:
        self._bus = bus
        self._config = config or IEC104ClientConfig()
        self._client: Optional[IEC104Client] = None
        self._rx_task: Optional[asyncio.Task[None]] = None
        self._stats: Dict[str, Any] = {"tx": 0, "rx": 0}
        self._lock = asyncio.Lock()

    @property
    def stats(self) -> Dict[str, Any]:
        return dict(self._stats)

    async def connect(self) -> None:
        async with self._lock:
            if self._client is not None:
                return
            self._client = IEC104Client(
                host=self._config.host,
                port=self._config.port,
                k=self._config.k,
                w=self._config.w,
                t0=self._config.t0,
                t1=self._config.t1,
                t2=self._config.t2,
                t3=self._config.t3,
            )
            connect_fn = getattr(self._client, 'connect', None)
            if connect_fn is None:
                raise RuntimeError('IEC104Client missing connect method')
            await asyncio.to_thread(connect_fn)
            self._rx_task = asyncio.create_task(self._receive_loop())
            logger.info("IEC104 client connected", extra={"host": self._config.host, "port": self._config.port})

    async def disconnect(self) -> None:
        async with self._lock:
            if self._client is None:
                return
            client = self._client
            self._client = None
            if self._rx_task:
                self._rx_task.cancel()
            disconnect_fn = getattr(client, 'disconnect', None)
            if disconnect_fn is not None:
                await asyncio.to_thread(disconnect_fn)
            logger.info("IEC104 client disconnected")

    async def send_asdu(self, asdu: Any) -> None:
        if self._client is None:
            raise RuntimeError("IEC104 client not connected")
        payload: bytes
        decoded_payload: Dict[str, Any]
        if isinstance(asdu, (bytes, bytearray)):
            payload = bytes(asdu)
            decoded_payload = {}
        else:
            payload = encode_asdu(asdu)
            decoded_payload = _serialize_asdu(asdu)
        send_fn = getattr(self._client, 'send', None)
        if send_fn is None:
            raise RuntimeError('IEC104Client missing send method')
        await asyncio.to_thread(send_fn, payload)
        self._stats["tx"] += 1
        self._bus.publish(
            FrameEvent.from_payload(
                role="client",
                direction="tx",
                apci=payload[:4],
                asdu=payload[4:],
                decoded=decoded_payload,
            )
        )

    async def _receive_loop(self) -> None:
        assert self._client is not None
        client = self._client
        while True:
            try:
                receive_fn = getattr(client, 'receive', None)
                if receive_fn is None:
                    await asyncio.sleep(1)
                    continue
                message = await asyncio.to_thread(receive_fn)
            except asyncio.CancelledError:  # pragma: no cover - cancelled during shutdown
                raise
            except Exception as exc:  # pragma: no cover - network errors
                logger.exception("IEC104 client receive loop failed: %s", exc)
                await asyncio.sleep(1)
                continue
            apci_bytes = getattr(message, "apci", b"") if message is not None else b""
            asdu_bytes = getattr(message, "asdu", b"") if message is not None else b""
            decoded: Dict[str, Any] = {}
            if isinstance(asdu_bytes, (bytes, bytearray)) and asdu_bytes:
                try:
                    decoded_obj = decode_asdu(asdu_bytes)
                    decoded = _serialize_asdu(decoded_obj)
                except Exception:  # pragma: no cover - decode best-effort
                    decoded = {"error": "decode_failed"}
            self._stats["rx"] += 1
            self._bus.publish(
                FrameEvent.from_payload(
                    role="client",
                    direction="rx",
                    apci=bytes(apci_bytes) if isinstance(apci_bytes, (bytes, bytearray)) else b"",
                    asdu=bytes(asdu_bytes) if isinstance(asdu_bytes, (bytes, bytearray)) else b"",
                    decoded=decoded,
                )
            )


def _serialize_asdu(asdu: Any) -> Dict[str, Any]:
    if asdu is None:
        return {}
    if is_dataclass(asdu):
        return asdict(asdu)
    if hasattr(asdu, "__dict__"):
        return dict(vars(asdu))
    if isinstance(asdu, dict):
        return asdu
    return {"repr": repr(asdu)}


__all__ = ["IEC104ClientService", "IEC104ClientConfig"]
