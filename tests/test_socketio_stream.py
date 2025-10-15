from __future__ import annotations

import asyncio
from datetime import datetime

import pytest

from app.socketio import socketio, stream_bus
from app.services.stream_bus import FramePayload


@pytest.mark.asyncio
async def test_socketio_stream_connection(app) -> None:
    test_client = socketio.test_client(app, namespace="/stream")
    assert test_client.is_connected("/stream")
    await stream_bus.publish(
        "stream",
        FramePayload(
            timestamp=datetime.utcnow(),
            role="client",
            direction="tx",
            apci_hex="0x01",
            asdu_hex="0x02",
            decoded={"ti": "M_SP_NA_1"},
        ),
    )
    await asyncio.sleep(0.05)
    received = test_client.get_received("/stream")
    assert any(packet["name"] in {"frames", "history"} for packet in received)
    test_client.disconnect(namespace="/stream")
