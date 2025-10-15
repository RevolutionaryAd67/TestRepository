"""File based storage helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


class FileStorage:
    """Simple helper for storing text files inside a base directory."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_text(self, relative: Path, content: str) -> Path:
        path = self.base_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def read_text(self, relative: Path) -> str:
        return (self.base_dir / relative).read_text(encoding="utf-8")

    def list_files(self, relative: Path | None = None) -> Iterable[Path]:
        root = self.base_dir if relative is None else self.base_dir / relative
        if not root.exists():
            return []
        return sorted(p for p in root.rglob("*") if p.is_file())


__all__ = ["FileStorage"]
