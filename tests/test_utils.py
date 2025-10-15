from app.utils.hex import bytes_to_hex, chunked_hex
from app.utils.time import utcnow_iso


def test_bytes_to_hex():
    assert bytes_to_hex(b"\x01\x02") == "01 02"


def test_chunked_hex():
    data = b"0123456789abcdef"
    chunks = list(chunked_hex(data, 4))
    assert chunks[0] == "30 31 32 33"


def test_utcnow_iso_format():
    value = utcnow_iso()
    assert value.endswith("Z") is False
    assert "T" in value
