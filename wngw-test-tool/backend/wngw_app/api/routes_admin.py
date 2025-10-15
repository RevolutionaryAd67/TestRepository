"""Administration endpoints."""

from __future__ import annotations

import json
from pathlib import Path

from ..config import AppSettings, get_settings
from ..domain.models import PartnerSettings

# Placeholder router implementations; actual FastAPI endpoints require FastAPI package.
class Router:
    def get(self, *_args, **_kwargs):  # pragma: no cover - placeholder for FastAPI
        return lambda func: func

    def put(self, *_args, **_kwargs):  # pragma: no cover - placeholder
        return lambda func: func


router = Router()


def _partner_file(settings: AppSettings) -> Path:
    return settings.data_dir / "partners.json"


@router.get("/partners")
def get_partners(settings: AppSettings | None = None) -> PartnerSettings:
    settings = settings or get_settings()
    path = _partner_file(settings)
    if not path.exists():
        return PartnerSettings(
            client_ip="127.0.0.1",
            client_port=2404,
            server_bind_ip="0.0.0.0",
            server_port=2404,
            common_address=1,
            language="de",
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    return PartnerSettings.from_dict(data)


@router.put("/partners")
def put_partners(payload: PartnerSettings, settings: AppSettings | None = None) -> PartnerSettings:
    settings = settings or get_settings()
    path = _partner_file(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload.to_dict(), indent=2), encoding="utf-8")
    return payload


__all__ = ["router", "get_partners", "put_partners"]
