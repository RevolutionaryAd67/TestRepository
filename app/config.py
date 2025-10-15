from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field, validator


class IECDefaults(BaseModel):
    host: str = Field("127.0.0.1", description="IEC-104 client target host")
    port: int = Field(2404, description="IEC-104 client target port")
    server_host: str = Field("0.0.0.0", description="IEC-104 server listen host")
    server_port: int = Field(2404, description="IEC-104 server listen port")
    k_window: int = Field(12, ge=1)
    w_window: int = Field(8, ge=1)
    t0: float = Field(30.0, gt=0)
    t1: float = Field(15.0, gt=0)
    t2: float = Field(10.0, gt=0)
    t3: float = Field(20.0, gt=0)


class AuthConfig(BaseModel):
    mode: str = Field("none", description="Authentication mode: none|basic")
    basic_username: Optional[str] = None
    basic_password: Optional[str] = None

    @validator("mode")
    def validate_mode(cls, value: str) -> str:
        allowed = {"none", "basic"}
        if value not in allowed:
            raise ValueError(f"Authentication mode must be one of {allowed}")
        return value

    @validator("basic_password", always=True)
    def password_required(cls, password: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        if values.get("mode") == "basic":
            if not password or not values.get("basic_username"):
                raise ValueError("basic auth requires username and password")
        return password


class StreamConfig(BaseModel):
    ringbuffer_size: int = Field(10_000, ge=100)
    max_client_rate_fps: int = Field(30, ge=1, le=120)
    history_page_size: int = Field(200, ge=50)


class DatabaseConfig(BaseModel):
    url: str = Field("sqlite:///app.db")
    echo: bool = False


class Settings(BaseModel):
    environment: str = Field(os.environ.get("FLASK_ENV", "production"))
    secret_key: str = Field(default_factory=lambda: os.environ.get("SECRET_KEY", "dev-secret"))
    iec: IECDefaults = Field(default_factory=IECDefaults)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    stream: StreamConfig = Field(default_factory=StreamConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    testing: bool = False
    log_level: str = Field("INFO")

    class Config:
        arbitrary_types_allowed = True


@dataclass
class ConfigLoader:
    settings: Settings
    source_path: Optional[Path] = None


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_settings(env_path: Optional[Path] = None, yaml_path: Optional[Path] = None) -> ConfigLoader:
    env_path = env_path or Path(".env")
    if env_path.exists():
        from dotenv import load_dotenv

        load_dotenv(env_path)

    yaml_data: Dict[str, Any] = {}
    if yaml_path:
        yaml_data = _load_yaml(yaml_path)

    settings = Settings(**yaml_data)
    return ConfigLoader(settings=settings, source_path=yaml_path)


__all__ = ["Settings", "load_settings", "ConfigLoader"]
