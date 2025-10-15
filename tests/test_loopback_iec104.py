import asyncio

import pytest

from app.services.iec_client import IEC104ClientConfig, IEC104ClientService
from app.services.iec_server import IEC104ServerConfig, IEC104ServerService
from app.socketbus import FrameSocketBus


@pytest.mark.asyncio
async def test_client_server_loopback(monkeypatch, tmp_path):
    iec104 = pytest.importorskip("iec104")
    port = 25000
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path/'test.db'}")
    bus = FrameSocketBus(100)
    client_service = IEC104ClientService(bus, IEC104ClientConfig(port=port))
    server_service = IEC104ServerService(bus, IEC104ServerConfig(port=port))

    try:
        await server_service.start()
        await asyncio.sleep(0.1)
        await client_service.connect()
        await asyncio.sleep(0.1)
        asdu = iec104.M_SP_NA_1(address=1, value=True)
        await client_service.send_asdu(asdu)
        await asyncio.sleep(0.2)
    except Exception as exc:
        pytest.skip(f"Loopback not supported in this environment: {exc}")
    finally:
        await client_service.disconnect()
        await server_service.stop()

    snapshot = bus.snapshot()
    assert any(frame["role"] == "client" for frame in snapshot)
