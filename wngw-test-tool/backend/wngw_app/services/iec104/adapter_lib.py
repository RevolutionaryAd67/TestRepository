"""Adapter wrapping the local IEC 60870-5-104 library."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Awaitable, Callable, Optional

from iec104 import (
    ASDUHeader,
    CauseOfTransmission,
    IEC104Client,
    IEC104Server,
    IEC104Session,
    SessionParameters,
    SingleCommand,
    SingleCommandASDU,
    TypeID,
)

from ...domain.events import APCIMetadata, ASDUDescriptor, IEC104FrameEvent
from ...domain.models import ProtocolEntry
from ..livebus import LiveBus
from ..protocol_store import ProtocolStore
from .contract import IEC104ClientAdapter, IEC104ServerAdapter

logger = logging.getLogger(__name__)


def _asdu_to_descriptor(asdu: object) -> ASDUDescriptor:
    if isinstance(asdu, SingleCommandASDU):
        ioa = asdu.information_objects[0].ioa if asdu.information_objects else None
        payload = {
            "value": asdu.information_objects[0].state if asdu.information_objects else None,
            "qualifier": asdu.information_objects[0].qualifier if asdu.information_objects else None,
        }
        return ASDUDescriptor(
            typeId=int(asdu.header.type_id),
            cause=int(asdu.header.cause),
            ca=asdu.header.common_address,
            ioa=ioa,
            payload=payload,
        )
    raise NotImplementedError("Unsupported ASDU type")


class IEC104LibClientAdapterImpl(IEC104ClientAdapter):
    """IEC-104 client wrapper."""

    def __init__(self, live_bus: LiveBus, protocol_store: ProtocolStore) -> None:
        self._live_bus = live_bus
        self._protocol_store = protocol_store
        self._client: Optional[IEC104Client] = None
        self._rx_callback: Optional[Callable[[IEC104FrameEvent], Awaitable[None]]] = None

    async def connect(self, host: str, port: int) -> None:
        logger.info("connecting", extra={"role": "client", "host": host, "port": port})
        self._client = await IEC104Client.connect(host, port, SessionParameters())

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def send_single_command(self, ca: int, ioa: int, value: bool) -> None:
        if self._client is None:
            raise RuntimeError("Client not connected")
        header = ASDUHeader(
            type_id=TypeID.C_SC_NA_1,
            sequence=False,
            vsq_number=1,
            cause=CauseOfTransmission.ACTIVATION,
            negative_confirm=False,
            test=False,
            originator_address=0,
            common_address=ca,
            oa=None,
        )
        command = SingleCommandASDU(
            header=header,
            information_objects=(SingleCommand(ioa=ioa, state=value, qualifier=0),),
        )
        await self._client.send_asdu(command)
        await self._emit_event("tx", command)
        entry = ProtocolEntry(
            timestamp=datetime.now(timezone.utc),
            result="sent-single-command",
            payload={"ca": ca, "ioa": ioa, "value": value},
        )
        self._protocol_store.append("single-command", entry)

    async def recv_once(self, timeout: float | None = None) -> object | None:
        if self._client is None:
            raise RuntimeError("Client not connected")
        try:
            asdu = await asyncio.wait_for(self._client.recv(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
        await self._emit_event("rx", asdu)
        return asdu

    def on_rx(self, callback: Callable[[IEC104FrameEvent], Awaitable[None]]) -> None:
        self._rx_callback = callback

    async def _emit_event(self, direction: str, asdu: object) -> None:
        descriptor = _asdu_to_descriptor(asdu)
        event = IEC104FrameEvent(
            role="client",
            dir=direction,
            ts=datetime.now(timezone.utc),
            apci=APCIMetadata(type="I", vs=-1, vr=-1),
            asdu=descriptor,
            raw=None,
        )
        await self._live_bus.publish(event)
        if self._rx_callback:
            await self._rx_callback(event)


class IEC104LibServerAdapterImpl(IEC104ServerAdapter):
    """IEC-104 server wrapper."""

    def __init__(self, live_bus: LiveBus) -> None:
        self._live_bus = live_bus
        self._server: Optional[IEC104Server] = None
        self._handler: Optional[Callable[[IEC104Session, object], Awaitable[None]]] = None

    async def start(self, bind_ip: str, port: int) -> None:
        if self._handler is None:
            raise RuntimeError("Handler not set")
        self._server = IEC104Server(bind_ip, port, self._wrapped_handler, SessionParameters())
        await self._server.start()
        logger.info("server started", extra={"role": "server", "bind_ip": bind_ip, "port": port})

    async def stop(self) -> None:
        if self._server is not None:
            await self._server.stop()
            self._server = None
            logger.info("server stopped", extra={"role": "server"})

    def set_handler(
        self,
        handler: Callable[[IEC104Session, object], Awaitable[None]],
    ) -> None:
        self._handler = handler

    async def _wrapped_handler(self, session: IEC104Session, asdu: object) -> None:
        await self._live_bus.publish(
            IEC104FrameEvent(
                role="server",
                dir="rx",
                ts=datetime.now(timezone.utc),
                apci=APCIMetadata(type="I", vs=-1, vr=-1),
                asdu=_asdu_to_descriptor(asdu),
                raw=None,
            )
        )
        if self._handler is None:
            raise RuntimeError("Handler not configured")
        await self._handler(session, asdu)


__all__ = ["IEC104LibClientAdapterImpl", "IEC104LibServerAdapterImpl"]
