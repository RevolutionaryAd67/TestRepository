"""Test execution endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from ..config import AppSettings, get_settings
from ..domain.models import ProtocolListEntry
from ..services.iec104 import factory
from ..services.protocol_store import ProtocolStore

router = APIRouter()


class SingleCommandPayload(BaseModel):
    host: str
    port: int = Field(ge=1, le=65535)
    ca: int = Field(ge=0, le=65535)
    ioa: int = Field(ge=0, le=16777215)
    value: bool


async def _protocol_store(settings: AppSettings = Depends(get_settings)) -> ProtocolStore:
    return ProtocolStore(settings.logs_dir)


@router.post("/single-command")
async def post_single_command(
    payload: SingleCommandPayload,
    request: Request,
    store: ProtocolStore = Depends(_protocol_store),
) -> dict[str, Any]:
    live_bus = request.app.state.live_bus
    client = factory.create_client(live_bus, store)
    await client.connect(payload.host, payload.port)
    try:
        await client.send_single_command(payload.ca, payload.ioa, payload.value)
        reply = await client.recv_once(timeout=0.1)
    except TimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    finally:
        await client.close()
    response = {"status": "ok"}
    if reply is not None:
        response["reply"] = "received"
    return response


@router.get("/protocols", response_model=list[ProtocolListEntry])
async def list_protocols(store: ProtocolStore = Depends(_protocol_store)) -> list[ProtocolListEntry]:
    return store.list_protocols()


__all__ = ["router"]
