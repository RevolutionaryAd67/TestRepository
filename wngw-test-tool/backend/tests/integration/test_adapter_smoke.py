"""Smoke test for IEC-104 adapters."""

from __future__ import annotations

import asyncio

from wngw_app.services.iec104 import factory
from wngw_app.services.livebus import LiveBus
from wngw_app.services.protocol_store import ProtocolStore


def test_client_server_start_stop(tmp_path):
    async def scenario() -> None:
        live_bus = LiveBus()
        store = ProtocolStore(tmp_path)
        client = factory.create_client(live_bus, store)
        server = factory.create_server(live_bus)

        async def handler(session, asdu):  # pragma: no cover - no-op handler
            del session, asdu

        server.set_handler(handler)
        await server.start("0.0.0.0", 2404)
        try:
            await client.connect("0.0.0.0", 2404)
        finally:
            await client.close()
            await server.stop()
            await live_bus.close()

    asyncio.run(scenario())
