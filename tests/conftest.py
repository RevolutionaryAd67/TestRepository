from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any, AsyncGenerator

import pytest

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.config import DatabaseConfig, IECDefaults, Settings
from app.services.iec_client import ClientConfiguration, IEC104ClientService
from app.services.iec_server import IEC104ServerService, ServerConfiguration


class FakeIECClient:
    def __init__(self) -> None:
        self._connected = False
        self.sent: list[Any] = []
        self.queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    async def connect(self, host: str, port: int, **_: Any) -> None:  # noqa: D401
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def send_asdu(self, asdu: Any) -> None:
        self.sent.append(asdu)

    async def receive(self) -> dict[str, Any]:
        return await self.queue.get()

    def connected(self) -> bool:
        return self._connected


class FakeIECServer:
    def __init__(self) -> None:
        self._active = False
        self.sent: list[Any] = []
        self.queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    async def listen(self, host: str, port: int, **_: Any) -> None:
        self._active = True

    async def close(self) -> None:
        self._active = False

    async def send_asdu(self, connection_id: str, asdu: Any) -> None:
        self.sent.append((connection_id, asdu))

    async def receive(self) -> dict[str, Any]:
        return await self.queue.get()


@pytest.fixture()
async def app() -> AsyncGenerator[Any, Any]:
    settings = Settings(
        testing=True,
        iec=IECDefaults(),
        database=DatabaseConfig(url="sqlite:///:memory:")
    )
    flask_app = create_app(settings)
    flask_app.iec_client = IEC104ClientService(  # type: ignore[attr-defined]
        ClientConfiguration(
            host=settings.iec.host,
            port=settings.iec.port,
            k_window=settings.iec.k_window,
            w_window=settings.iec.w_window,
            t0=settings.iec.t0,
            t1=settings.iec.t1,
            t2=settings.iec.t2,
            t3=settings.iec.t3,
        ),
        client_factory=FakeIECClient,
    )
    flask_app.iec_server = IEC104ServerService(  # type: ignore[attr-defined]
        ServerConfiguration(host=settings.iec.server_host, port=settings.iec.server_port),
        server_factory=FakeIECServer,
    )
    async with flask_app.app_context():
        yield flask_app


@pytest.fixture()
async def client(app: Any) -> AsyncIterator[Any]:
    async with app.test_async_client() as test_client:
        yield test_client
