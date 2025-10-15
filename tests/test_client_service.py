from __future__ import annotations

import asyncio
from typing import Any

import pytest

from app.services import iec_client
from app.socketio import stream_bus


@pytest.mark.asyncio
async def test_client_service_send_receive(app: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    service = app.iec_client  # type: ignore[attr-defined]
    monkeypatch.setattr(iec_client, "encode_asdu", lambda **kwargs: kwargs)
    await service.connect()
    fake_client = service._client  # type: ignore[attr-defined]
    assert fake_client is not None

    await fake_client.queue.put(
        {
            "decoded": {"ti": "M_SP_NA_1", "cot": "3", "ns": 1, "nr": 2},
            "apci_hex": "0x01",
            "asdu_hex": "0x02",
        }
    )
    await asyncio.sleep(0.05)
    await service.send_asdu({"ti": "M_SP_NA_1", "cot": "3", "ioa": "1", "values": []})
    await asyncio.sleep(0.05)
    assert service.metrics.sent_frames == 1
    assert service.metrics.received_frames >= 1
    history = await stream_bus.history(limit=10)
    assert any(frame.role == "client" for frame in history)
    await service.disconnect()
