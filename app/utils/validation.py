from __future__ import annotations

from typing import Iterable, List, Sequence

from pydantic import BaseModel, ValidationError, field_validator


class SignalRow(BaseModel):
    name: str
    ti: str
    ioa: str
    scale: str | None = None
    unit: str | None = None
    default: str | None = None
    description: str | None = None

    @field_validator("name", "ti", "ioa")
    @classmethod
    def not_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value


def validate_signal_rows(rows: Sequence[dict[str, str | None]]) -> List[SignalRow]:
    validated: List[SignalRow] = []
    for index, row in enumerate(rows):
        try:
            validated.append(SignalRow(**row))
        except ValidationError as exc:
            raise ValueError(f"Invalid row {index}: {exc}") from exc
    return validated


__all__ = ["SignalRow", "validate_signal_rows"]
