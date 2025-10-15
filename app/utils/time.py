"""Time formatting utilities."""
from __future__ import annotations

from datetime import datetime, timezone


def utcnow_iso() -> str:
    """Return current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()
