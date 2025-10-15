"""Definitions of live events streamed via WebSocket."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Literal, Optional

Role = Literal["client", "server"]
Direction = Literal["tx", "rx"]
APCIType = Literal["I", "S", "U"]


@dataclass
class APCIMetadata:
    type: APCIType
    vs: int = -1
    vr: int = -1


@dataclass
class ASDUDescriptor:
    typeId: int
    cause: int
    ca: int
    ioa: Optional[int]
    payload: dict[str, Any]


@dataclass
class IEC104FrameEvent:
    kind: str
    role: Role
    dir: Direction
    ts: datetime
    apci: APCIMetadata
    asdu: ASDUDescriptor
    raw: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["ts"] = self.ts.isoformat()
        return data
