"""Simple JSONL based protocol store."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

from ..domain.models import ProtocolEntry, ProtocolListEntry


class ProtocolStore:
    """Persist protocol entries as JSON lines."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _file_path(self, name: str) -> Path:
        return self.base_dir / f"{name}.jsonl"

    def append(self, name: str, entry: ProtocolEntry) -> Path:
        path = self._file_path(name)
        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry.to_dict()))
            file.write("\n")
        return path

    def list_protocols(self) -> list[ProtocolListEntry]:
        entries: list[ProtocolListEntry] = []
        for file in sorted(self.base_dir.glob("*.jsonl")):
            stat = file.stat()
            entries.append(
                ProtocolListEntry(
                    path=file.name,
                    created_at=datetime.fromtimestamp(stat.st_mtime),
                    description=None,
                )
            )
        return entries

    def read(self, name: str) -> Iterable[ProtocolEntry]:
        path = self._file_path(name)
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    data = json.loads(line)
                    yield ProtocolEntry.from_dict(data)


__all__ = ["ProtocolStore"]
