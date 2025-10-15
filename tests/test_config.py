from __future__ import annotations

from app.config import Settings


def test_settings_defaults() -> None:
    settings = Settings()
    assert settings.iec.host == "127.0.0.1"
    assert settings.stream.ringbuffer_size == 10_000
    assert settings.auth.mode == "none"
