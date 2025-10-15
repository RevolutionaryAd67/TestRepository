"""Domain data transfer objects."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Optional


def _ensure_range(value: int, *, minimum: int, maximum: int) -> int:
    if not (minimum <= value <= maximum):
        raise ValueError(f"Value {value} outside range {minimum}-{maximum}")
    return value


def _ensure_language(value: str) -> str:
    if value not in {"de", "en"}:
        raise ValueError("language must be 'de' or 'en'")
    return value


@dataclass
class PartnerSettings:
    client_ip: str
    client_port: int
    server_bind_ip: str
    server_port: int
    common_address: int
    language: str = "de"

    def __post_init__(self) -> None:
        self.client_port = _ensure_range(self.client_port, minimum=0, maximum=65535)
        self.server_port = _ensure_range(self.server_port, minimum=0, maximum=65535)
        self.common_address = _ensure_range(self.common_address, minimum=0, maximum=65535)
        self.language = _ensure_language(self.language)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PartnerSettings":
        return cls(**data)


@dataclass
class ProtocolEntry:
    timestamp: datetime
    result: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProtocolEntry":
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            result=data["result"],
            payload=data["payload"],
        )


@dataclass
class ProtocolListEntry:
    path: str
    created_at: datetime
    description: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data
