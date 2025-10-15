from app.config import AppSettings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("APP_NAME", raising=False)
    settings = AppSettings()
    assert settings.app_name == "IEC104 Webtester"
    assert settings.stream_ringbuffer_capacity == 10_000
