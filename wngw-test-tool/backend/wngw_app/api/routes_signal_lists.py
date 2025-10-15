"""Signal list upload endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from ..config import AppSettings, get_settings
from ..services.signal_lists import SignalListError, read_signal_list

router = APIRouter()


@router.post("/upload")
async def upload_signal_list(
    file: UploadFile = File(...),
    settings: AppSettings = Depends(get_settings),
) -> dict[str, object]:
    destination = settings.uploads_dir / file.filename
    try:
        result = read_signal_list(file, destination)
    except SignalListError as exc:
        return {"status": "error", "detail": str(exc)}
    return {"status": "ok", "data": result}


__all__ = ["router"]
