from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Protocol

try:
    from iec104 import IEC104Client, decode_asdu, encode_asdu
    from iec104.asdu import ASDU  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    class ASDU:  # type: ignore[override]
        pass

    class IEC104Client:  # type: ignore[override]
        async def connect(self, *args: Any, **kwargs: Any) -> None: ...

        async def disconnect(self) -> None: ...

        async def send_asdu(self, asdu: ASDU) -> None: ...

        async def receive(self) -> Dict[str, Any]: ...

        def connected(self) -> bool: ...

    def encode_asdu(*args: Any, **kwargs: Any) -> ASDU:  # type: ignore[misc]
        raise NotImplementedError

    def decode_asdu(asdu: ASDU) -> Dict[str, Any]:  # type: ignore[misc]
        return {}


from ..socketio import emit_frame
from .stream_bus import FramePayload


class IEC104ClientProtocol(Protocol):
    async def connect(self, host: str, port: int, **kwargs: Any) -> None: ...

    async def disconnect(self) -> None: ...

    async def send_asdu(self, asdu: ASDU) -> None: ...

    async def receive(self) -> Dict[str, Any]: ...

    def connected(self) -> bool: ...


@dataclass(slots=True)
class ClientConfiguration:
    host: str
    port: int
    k_window: int
    w_window: int
    t0: float
    t1: float
    t2: float
    t3: float


@dataclass(slots=True)
class ClientMetrics:
    connected: bool = False
    sent_frames: int = 0
    received_frames: int = 0
    last_ns: Optional[int] = None
    last_nr: Optional[int] = None
    last_activity: Optional[datetime] = None


class IEC104ClientService:
    def __init__(
        self,
        config: ClientConfiguration,
        client_factory: type[IEC104ClientProtocol] = IEC104Client,  # type: ignore[assignment]
    ) -> None:
        self._config = config
        self._client_factory = client_factory
        self._client: Optional[IEC104ClientProtocol] = None
        self._receiver_task: Optional[asyncio.Task[None]] = None
        self.metrics = ClientMetrics()
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        async with self._lock:
            if self._client and self._client.connected():
                return
            self._client = self._client_factory()
            await self._client.connect(
                self._config.host,
                self._config.port,
                k=self._config.k_window,
                w=self._config.w_window,
                t0=self._config.t0,
                t1=self._config.t1,
                t2=self._config.t2,
                t3=self._config.t3,
            )
            self.metrics.connected = True
            self.metrics.last_activity = datetime.utcnow()
            loop = asyncio.get_running_loop()
            self._receiver_task = loop.create_task(self._receiver_loop())

    async def disconnect(self) -> None:
        async with self._lock:
            if not self._client:
                return
            try:
                await self._client.disconnect()
            finally:
                self.metrics.connected = False
                if self._receiver_task:
                    self._receiver_task.cancel()
                self._client = None

    async def send_asdu(self, payload: Dict[str, Any]) -> None:
        async with self._lock:
            if not self._client:
                raise RuntimeError("Client not connected")
            asdu = encode_asdu(**payload)
            await self._client.send_asdu(asdu)
            self.metrics.sent_frames += 1
            decoded_payload = {**payload}
            decoded_payload.pop("apci_hex", None)
            decoded_payload.pop("asdu_hex", None)
            await emit_frame(
                FramePayload(
                    timestamp=datetime.utcnow(),
                    role="client",
                    direction="tx",
                    apci_hex=payload.get("apci_hex", ""),
                    asdu_hex=payload.get("asdu_hex", ""),
                    decoded=decoded_payload,
                )
            )

    async def _receiver_loop(self) -> None:
        assert self._client is not None
        try:
            while self._client.connected():
                frame = await self._client.receive()
                decoded = frame.get("decoded") or {}
                self.metrics.received_frames += 1
                self.metrics.last_activity = datetime.utcnow()
                self.metrics.last_ns = decoded.get("ns")
                self.metrics.last_nr = decoded.get("nr")
                await emit_frame(
                    FramePayload(
                        timestamp=datetime.utcnow(),
                        role="client",
                        direction="rx",
                        apci_hex=frame.get("apci_hex", ""),
                        asdu_hex=frame.get("asdu_hex", ""),
                        decoded=decoded,
                    )
                )
        except asyncio.CancelledError:
            return
        except Exception as exc:  # pragma: no cover - defensive
            await emit_frame(
                FramePayload(
                    timestamp=datetime.utcnow(),
                    role="client",
                    direction="rx",
                    apci_hex="",
                    asdu_hex="",
                    decoded={"error": str(exc)},
                )
            )


__all__ = ["IEC104ClientService", "ClientConfiguration", "ClientMetrics"]
