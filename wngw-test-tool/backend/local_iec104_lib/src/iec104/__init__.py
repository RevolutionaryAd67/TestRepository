"""Minimal IEC 60870-5-104 implementation for testing purposes."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import IntEnum
from typing import Awaitable, Callable, Iterable, Optional, Protocol

__all__ = [
    "ASDUType",
    "CauseOfTransmission",
    "CP56Time2a",
    "IEC104Client",
    "IEC104Server",
    "IEC104Session",
    "SessionParameters",
    "StreamingAPDUDecoder",
    "TypeID",
    "ASDUHeader",
    "SingleCommand",
    "SingleCommandASDU",
    "build_i_frame",
    "decode_apdu",
    "decode_asdu",
    "encode_asdu",
]


class TypeID(IntEnum):
    M_SP_NA_1 = 1
    M_SP_TB_1 = 2
    M_ME_NC_1 = 13
    C_SC_NA_1 = 45


class CauseOfTransmission(IntEnum):
    ACTIVATION = 6
    SPONTANEOUS = 3


@dataclass(slots=True)
class SessionParameters:
    originator_address: int = 0

    def with_oa(self, oa: int) -> "SessionParameters":
        return SessionParameters(originator_address=oa)


@dataclass(slots=True)
class CP56Time2a:
    milliseconds: int
    minute: int
    invalid: bool
    hour: int
    summer_time: bool
    day_of_month: int
    day_of_week: int
    month: int
    year: int

    def to_datetime(self):  # pragma: no cover - placeholder
        raise NotImplementedError

    @classmethod
    def from_datetime(cls, dt, *, summer_time: bool = False):  # pragma: no cover
        raise NotImplementedError

    def encode(self):  # pragma: no cover - placeholder
        raise NotImplementedError

    @classmethod
    def decode(cls, view):  # pragma: no cover - placeholder
        raise NotImplementedError


class ASDUHeader:
    def __init__(
        self,
        *,
        type_id: TypeID,
        sequence: bool,
        vsq_number: int,
        cause: CauseOfTransmission,
        negative_confirm: bool,
        test: bool,
        originator_address: int,
        common_address: int,
        oa: Optional[int],
    ) -> None:
        self.type_id = type_id
        self.sequence = sequence
        self.vsq_number = vsq_number
        self.cause = cause
        self.negative_confirm = negative_confirm
        self.test = test
        self.originator_address = originator_address
        self.common_address = common_address
        self.oa = oa


class InformationObject(Protocol):
    ioa: int


ASDUType = object


class SingleCommand:
    def __init__(self, *, ioa: int, state: bool, qualifier: int) -> None:
        self.ioa = ioa
        self.state = state
        self.qualifier = qualifier


class SingleCommandASDU:
    def __init__(self, *, header: ASDUHeader, information_objects: Iterable[SingleCommand]) -> None:
        self.header = header
        self.information_objects = list(information_objects)


class IEC104Session:
    """Session abstraction using in-memory queues."""

    def __init__(self, role: str) -> None:
        self.role = role
        self._rx: asyncio.Queue[object] = asyncio.Queue()
        self._tx_callbacks: list[Callable[[object], Awaitable[None]]] = []

    async def send_asdu(self, asdu: object) -> None:
        for callback in list(self._tx_callbacks):
            await callback(asdu)

    async def recv(self) -> object:
        return await self._rx.get()

    async def close(self) -> None:
        while not self._rx.empty():
            self._rx.get_nowait()

    def register_tx(self, callback: Callable[[object], Awaitable[None]]) -> None:
        self._tx_callbacks.append(callback)

    async def deliver(self, asdu: object) -> None:
        await self._rx.put(asdu)


ASDUHandler = Callable[["IEC104Session", object], Awaitable[None]]


class IEC104Server:
    def __init__(
        self,
        host: str,
        port: int,
        handler: ASDUHandler,
        params: SessionParameters | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.handler = handler
        self.params = params or SessionParameters()
        self._started = False
        self._sessions: list[IEC104Session] = []

    async def start(self) -> None:
        if self._started:
            return
        _SERVERS[(self.host, self.port)] = self
        self._started = True

    async def stop(self) -> None:
        if not self._started:
            return
        _SERVERS.pop((self.host, self.port), None)
        for session in list(self._sessions):
            await session.close()
        self._sessions.clear()
        self._started = False

    async def _handle_client(self, server_session: IEC104Session, asdu: object) -> None:
        await server_session.deliver(asdu)
        await self.handler(server_session, asdu)


_SERVERS: dict[tuple[str, int], IEC104Server] = {}


class IEC104Client:
    def __init__(self, session: IEC104Session) -> None:
        self._session = session

    @classmethod
    async def connect(
        cls, host: str, port: int, params: SessionParameters | None = None
    ) -> "IEC104Client":
        del params
        server = _SERVERS.get((host, port))
        if server is None:
            raise ConnectionError("No IEC104Server listening")

        client_session = IEC104Session("client")
        server_session = IEC104Session("server")

        async def forward_to_server(asdu: object) -> None:
            await server._handle_client(server_session, asdu)

        client_session.register_tx(forward_to_server)
        server_session.register_tx(client_session.deliver)

        server._sessions.append(server_session)
        return cls(client_session)

    async def send_asdu(self, asdu: object) -> None:
        await self._session.send_asdu(asdu)

    async def recv(self) -> object:
        return await self._session.recv()

    async def close(self) -> None:
        await self._session.close()

    @property
    def session(self) -> IEC104Session:
        return self._session


class StreamingAPDUDecoder:  # pragma: no cover - placeholder
    def __init__(self) -> None:
        self.buffer: list[bytes] = []

    def feed(self, data: bytes) -> None:
        self.buffer.append(data)


def build_i_frame(asdu_bytes: bytes, send_seq: int, recv_seq: int) -> bytes:  # pragma: no cover
    del send_seq, recv_seq
    return asdu_bytes


def decode_apdu(apdu: bytes):  # pragma: no cover
    raise NotImplementedError("TODO decode_apdu integration")


def encode_asdu(asdu: object) -> bytes:  # pragma: no cover
    raise NotImplementedError


def decode_asdu(data: bytes) -> object:  # pragma: no cover
    raise NotImplementedError
