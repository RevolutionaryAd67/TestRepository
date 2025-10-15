"""Application configuration using Pydantic."""
from __future__ import annotations

from ipaddress import IPv4Address
from typing import Literal

from pydantic import BaseSettings, Field, validator


class AppSettings(BaseSettings):
    """Settings pulled from environment variables and .env files."""

    app_name: str = Field("IEC104 Webtester", alias="APP_NAME")
    app_host: str = Field("127.0.0.1", alias="APP_HOST")
    app_port: int = Field(8080, alias="APP_PORT")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    database_url: str = Field("sqlite+aiosqlite:///./iec104.db", alias="DATABASE_URL")

    iec104_client_host: str = Field("127.0.0.1", alias="IEC104_CLIENT_HOST")
    iec104_client_port: int = Field(2404, alias="IEC104_CLIENT_PORT")

    iec104_server_host: str = Field("0.0.0.0", alias="IEC104_SERVER_HOST")
    iec104_server_port: int = Field(2404, alias="IEC104_SERVER_PORT")

    basic_auth_enabled: bool = Field(False, alias="BASIC_AUTH_ENABLED")
    basic_auth_username: str = Field("admin", alias="BASIC_AUTH_USERNAME")
    basic_auth_password: str = Field("secret", alias="BASIC_AUTH_PASSWORD")

    stream_ringbuffer_capacity: int = Field(10_000, alias="STREAM_RINGBUFFER_CAPACITY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("app_port", "iec104_client_port", "iec104_server_port")
    def _validate_port(cls, value: int) -> int:
        if not 0 < value < 65536:
            raise ValueError("Port must be between 1 and 65535")
        return value

    @validator("stream_ringbuffer_capacity")
    def _validate_capacity(cls, value: int) -> int:
        if value < 100:
            raise ValueError("Ringbuffer capacity must be at least 100")
        return value
