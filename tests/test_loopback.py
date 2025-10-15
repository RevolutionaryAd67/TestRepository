from __future__ import annotations

import asyncio
from typing import Any

import pytest

from app.services import iec_client, iec_server
from app.socketio import stream_bus


@pytest.mark.asyncio
async def test_loopback_flow(app: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    client_service = app.iec_client  # type: ignore[attr-defined]
    server_service = app.iec_server  # type: ignore[attr-defined]
    monkeypatch.setattr(iec_client, "encode_asdu", lambda **kwargs: kwargs)
    monkeypatch.setattr(iec_server, "encode_asdu", lambda **kwargs: kwargs)

    await server_service.start()
    await client_service.connect()

    fake_server = server_service._server  # type: ignore[attr-defined]
    fake_client = client_service._client  # type: ignore[attr-defined]
    assert fake_server is not None and fake_client is not None

    await fake_server.queue.put(
        {
            "decoded": {"ti": "M_SP_NA_1", "cot": "3", "ioa": [1]},
            "apci_hex": "0x11",
            "asdu_hex": "0x22",
        }
    )
    await fake_client.queue.put(
        {
            "decoded": {"ti": "M_SP_TB_1", "cot": "3", "ioa": [2]},
            "apci_hex": "0x33",
            "asdu_hex": "0x44",
        }
    )
    await asyncio.sleep(0.05)

    await server_service.send_asdu("loop", {"ti": "C_SC_NA_1", "cot": "6", "ioa": "1", "values": []})
    await client_service.send_asdu({"ti": "C_SC_NA_1", "cot": "6", "ioa": "1", "values": []})
    await asyncio.sleep(0.05)

    history = await stream_bus.history(limit=50)
    roles = {frame.role for frame in history}
    assert {"client", "server"}.issubset(roles)

    await client_service.disconnect()
    await server_service.stop()
