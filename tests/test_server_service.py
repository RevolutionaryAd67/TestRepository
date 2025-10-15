from __future__ import annotations

import asyncio
from typing import Any

import pytest

from app.services import iec_server
from app.socketio import stream_bus


@pytest.mark.asyncio
async def test_server_service_receive(app: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    service = app.iec_server  # type: ignore[attr-defined]
    monkeypatch.setattr(iec_server, "encode_asdu", lambda **kwargs: kwargs)
    await service.start()
    fake_server = service._server  # type: ignore[attr-defined]
    assert fake_server is not None

    await fake_server.queue.put(
        {
            "decoded": {"ti": "M_SP_NA_1", "cot": "3"},
            "apci_hex": "0x10",
            "asdu_hex": "0x20",
        }
    )
    await asyncio.sleep(0.05)
    await service.send_asdu("conn-1", {"ti": "M_SP_NA_1", "cot": "3", "ioa": "1", "values": []})
    await asyncio.sleep(0.05)
    assert service.metrics.sent_frames == 1
    assert service.metrics.received_frames >= 1
    history = await stream_bus.history(limit=10)
    assert any(frame.role == "server" for frame in history)
    await service.stop()
