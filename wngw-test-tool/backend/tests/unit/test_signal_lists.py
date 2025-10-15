"""Tests for signal list processing."""

from __future__ import annotations

import io

from openpyxl import Workbook

from wngw_app.services.signal_lists import SupportsUploadFile, SignalListError, read_signal_list


class DummyUploadFile:
    def __init__(self, filename: str, buffer: io.BytesIO) -> None:
        self.filename = filename
        self.file = buffer


def create_upload(rows: list[dict[str, object]], name: str) -> SupportsUploadFile:
    wb = Workbook()
    ws = wb.active
    ws.append(["IOA", "Bezeichnung", "Einheit"])
    for row in rows:
        ws.append([row["IOA"], row["Bezeichnung"], row["Einheit"]])
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return DummyUploadFile(name, buffer)


def test_read_signal_list_success(tmp_path):
    upload = create_upload(
        [
            {"IOA": 1, "Bezeichnung": "Signal A", "Einheit": "A"},
            {"IOA": 2, "Bezeichnung": "Signal B", "Einheit": "B"},
        ],
        "signals.xlsx",
    )
    destination = tmp_path / upload.filename
    result = read_signal_list(upload, destination)
    assert result["records"][0]["ioa"] == 1


def test_read_signal_list_missing_column(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.append(["IOA", "Bezeichnung"])
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    upload = DummyUploadFile("missing.xlsx", buffer)
    destination = tmp_path / upload.filename
    try:
        read_signal_list(upload, destination)
    except SignalListError as exc:
        assert "Missing required columns" in str(exc)
    else:  # pragma: no cover - ensures exception is raised
        raise AssertionError("SignalListError expected")
