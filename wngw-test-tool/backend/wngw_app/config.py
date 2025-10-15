"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass
class AppSettings:
    api_prefix: str = "/api"
    websocket_path: str = "/ws/live"
    cors_origins: tuple[str, ...] = ("http://localhost:5173",)
    data_dir: Path = Path("data")
    uploads_dir: Path = Path("data/uploads")
    parsed_dir: Path = Path("data/parsed")
    logs_dir: Path = Path("data/logs/backend")

    def ensure_directories(self) -> None:
        for directory in (self.data_dir, self.uploads_dir, self.parsed_dir, self.logs_dir):
            directory.mkdir(parents=True, exist_ok=True)


def _load_settings() -> AppSettings:
    cors = tuple(filter(None, os.environ.get("WNGW_CORS", "http://localhost:5173").split(",")))
    settings = AppSettings(cors_origins=cors)
    settings.ensure_directories()
    return settings


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return _load_settings()


__all__ = ["AppSettings", "get_settings"]
