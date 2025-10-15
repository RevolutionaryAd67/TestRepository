from __future__ import annotations

from datetime import datetime

import pytest

from app.services.stream_bus import FrameFilter, FramePayload, StreamBus


@pytest.mark.asyncio
async def test_stream_bus_filters_and_history() -> None:
    bus = StreamBus(history_limit=5, queue_limit=2)
    payloads = [
        FramePayload(
            timestamp=datetime.utcnow(),
            role="client",
            direction="tx",
            apci_hex=f"0x{i}",
            asdu_hex=f"0xA{i}",
            decoded={"ti": "M_SP_NA_1", "cot": "3", "ioa": [i]},
        )
        for i in range(6)
    ]
    for payload in payloads:
        await bus.publish("stream", payload)

    await bus.subscribe("test")
    await bus.update_filters("test", direction="tx")

    await bus.publish(
        "stream",
        FramePayload(
            timestamp=datetime.utcnow(),
            role="client",
            direction="rx",
            apci_hex="0xff",
            asdu_hex="0xff",
            decoded={"ti": "M_SP_NA_1", "cot": "3", "ioa": [1]},
        ),
    )
    await bus.publish(
        "stream",
        FramePayload(
            timestamp=datetime.utcnow(),
            role="server",
            direction="tx",
            apci_hex="0xaa",
            asdu_hex="0xaa",
            decoded={"ti": "M_SP_NA_1", "cot": "3", "ioa": [1]},
        ),
    )

    batch = await bus.get_filtered_batch("test", max_items=5)
    assert all(item.direction == "tx" for item in batch)
    history = await bus.history(limit=5)
    assert len(history) == 5
