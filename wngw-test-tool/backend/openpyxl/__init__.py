"""Minimal openpyxl stub for offline testing."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence

__all__ = ["Workbook", "load_workbook"]


@dataclass
class Cell:
    value: object | None


class Worksheet:
    def __init__(self) -> None:
        self._rows: list[list[object | None]] = []

    def append(self, row: Sequence[object | None]) -> None:
        self._rows.append(list(row))

    def iter_rows(
        self,
        *,
        max_row: int | None = None,
        min_row: int | None = None,
    ) -> Iterator[list[Cell]]:
        start = 0 if min_row is None else max(min_row - 1, 0)
        end = len(self._rows) if max_row is None else min(max_row, len(self._rows))
        for row in self._rows[start:end]:
            yield [Cell(value=item) for item in row]


class Workbook:
    def __init__(self) -> None:
        self._active = Worksheet()

    @property
    def active(self) -> Worksheet:
        return self._active

    def save(self, target) -> None:
        data = self._active._rows
        if hasattr(target, "write"):
            target.write(json.dumps(data).encode("utf-8"))
        else:
            Path(target).write_bytes(json.dumps(data).encode("utf-8"))


class _LoadedWorkbook(Workbook):
    def __init__(self, rows: list[list[object | None]]) -> None:
        super().__init__()
        self._active._rows = rows


def load_workbook(filename, read_only: bool = False, data_only: bool = False) -> Workbook:
    if hasattr(filename, "read"):
        content = filename.read()
        rows = json.loads(content)
    else:
        rows = json.loads(Path(filename).read_text(encoding="utf-8"))
    return _LoadedWorkbook(rows)
