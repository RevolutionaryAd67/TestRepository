"""Factory helpers for IEC-104 adapters."""

from __future__ import annotations

from ..livebus import LiveBus
from ..protocol_store import ProtocolStore
from .adapter_lib import IEC104LibClientAdapterImpl, IEC104LibServerAdapterImpl
from .contract import IEC104ClientAdapter, IEC104ServerAdapter


def create_client(live_bus: LiveBus, protocol_store: ProtocolStore) -> IEC104ClientAdapter:
    return IEC104LibClientAdapterImpl(live_bus, protocol_store)


def create_server(live_bus: LiveBus) -> IEC104ServerAdapter:
    return IEC104LibServerAdapterImpl(live_bus)


__all__ = ["create_client", "create_server"]
