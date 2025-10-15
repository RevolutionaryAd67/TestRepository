from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Protocol

try:
    from iec104 import IEC104Server, decode_asdu, encode_asdu
    from iec104.asdu import ASDU  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    class ASDU:  # type: ignore[override]
        pass

    class IEC104Server:  # type: ignore[override]
        async def listen(self, *args: Any, **kwargs: Any) -> None: ...

        async def close(self) -> None: ...

        async def send_asdu(self, connection_id: str, asdu: ASDU) -> None: ...

        async def receive(self) -> Dict[str, Any]: ...

    def encode_asdu(*args: Any, **kwargs: Any) -> ASDU:  # type: ignore[misc]
        raise NotImplementedError

    def decode_asdu(asdu: ASDU) -> Dict[str, Any]:  # type: ignore[misc]
        return {}


from ..socketio import emit_frame
from .stream_bus import FramePayload


class IEC104ServerProtocol(Protocol):
    async def listen(self, host: str, port: int, **kwargs: Any) -> None: ...

    async def close(self) -> None: ...

    async def send_asdu(self, connection_id: str, asdu: ASDU) -> None: ...

    async def receive(self) -> Dict[str, Any]: ...


@dataclass(slots=True)
class ServerConfiguration:
    host: str
    port: int


@dataclass(slots=True)
class ServerMetrics:
    active: bool = False
    connections: int = 0
    sent_frames: int = 0
    received_frames: int = 0
    last_activity: Optional[datetime] = None


class IEC104ServerService:
    def __init__(
        self,
        config: ServerConfiguration,
        server_factory: type[IEC104ServerProtocol] = IEC104Server,  # type: ignore[assignment]
    ) -> None:
        self._config = config
        self._server_factory = server_factory
        self._server: Optional[IEC104ServerProtocol] = None
        self._loop_task: Optional[asyncio.Task[None]] = None
        self.metrics = ServerMetrics()
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        async with self._lock:
            if self._server:
                return
            self._server = self._server_factory()
            await self._server.listen(self._config.host, self._config.port)
            self.metrics.active = True
            self.metrics.last_activity = datetime.utcnow()
            loop = asyncio.get_running_loop()
            self._loop_task = loop.create_task(self._receiver_loop())

    async def stop(self) -> None:
        async with self._lock:
            if not self._server:
                return
            try:
                await self._server.close()
            finally:
                if self._loop_task:
                    self._loop_task.cancel()
                self.metrics.active = False
                self._server = None

    async def send_asdu(self, connection_id: str, payload: Dict[str, Any]) -> None:
        async with self._lock:
            if not self._server:
                raise RuntimeError("Server not active")
            asdu = encode_asdu(**payload)
            await self._server.send_asdu(connection_id, asdu)
            self.metrics.sent_frames += 1
            await emit_frame(
                FramePayload(
                    timestamp=datetime.utcnow(),
                    role="server",
                    direction="tx",
                    apci_hex=payload.get("apci_hex", ""),
                    asdu_hex=payload.get("asdu_hex", ""),
                    decoded={**payload},
                )
            )

    async def _receiver_loop(self) -> None:
        assert self._server is not None
        try:
            while True:
                frame = await self._server.receive()
                decoded = frame.get("decoded") or {}
                if not decoded and (asdu := frame.get("asdu")) is not None:
                    try:
                        decoded = decode_asdu(asdu)  # type: ignore[arg-type]
                    except Exception:  # pragma: no cover - defensive
                        decoded = {}
                self.metrics.received_frames += 1
                self.metrics.last_activity = datetime.utcnow()
                await emit_frame(
                    FramePayload(
                        timestamp=datetime.utcnow(),
                        role="server",
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
                    role="server",
                    direction="rx",
                    apci_hex="",
                    asdu_hex="",
                    decoded={"error": str(exc)},
                )
            )


__all__ = ["IEC104ServerService", "ServerConfiguration", "ServerMetrics"]
