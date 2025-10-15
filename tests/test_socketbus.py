import asyncio

import pytest

from app.socketbus import FrameEvent, FrameSocketBus


@pytest.mark.asyncio
async def test_ringbuffer_drop_oldest():
    bus = FrameSocketBus(5)
    queue = bus.register()
    for idx in range(10):
        bus.publish(
            FrameEvent.from_payload(
                role="client",
                direction="tx",
                apci=b"\x00\x00\x00\x00",
                asdu=bytes([idx]),
                decoded={"ti": idx},
            )
        )
    messages = [await queue.get() for _ in range(5)]
    assert messages[0]["decoded"]["ti"] == 5
