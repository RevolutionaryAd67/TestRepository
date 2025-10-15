"""Utility helpers for hexadecimal formatting."""
from __future__ import annotations

from typing import Iterable


def bytes_to_hex(data: bytes) -> str:
    """Return a spaced hex string representation."""
    return " ".join(f"{byte:02X}" for byte in data)


def chunked_hex(data: bytes, chunk_size: int = 16) -> Iterable[str]:
    for index in range(0, len(data), chunk_size):
        yield bytes_to_hex(data[index : index + chunk_size])
