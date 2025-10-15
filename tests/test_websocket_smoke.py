import pytest

from app import create_app
from app.socketbus import FrameEvent


@pytest.mark.asyncio
async def test_websocket_receives_bus_events(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path/'test.db'}")
    app = create_app()
    async with app.test_app() as test_app:
        bus = test_app.app.frame_bus
        async with test_app.test_websocket("/stream") as ws:
            bus.publish(
                FrameEvent.from_payload(
                    role="client",
                    direction="tx",
                    apci=b"\x68\x04\x00\x00",
                    asdu=b"\x01\x02\x03\x04",
                    decoded={"ti": 1, "cot": 3, "ioas": [1], "values": [True]},
                )
            )
            message = await ws.receive_json()
            assert message['role'] == 'client'
