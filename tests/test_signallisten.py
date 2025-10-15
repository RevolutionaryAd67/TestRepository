from __future__ import annotations

import json

import pytest


@pytest.mark.asyncio
async def test_signallist_import_export(client) -> None:
    payload = [
        {
            "name": "Signal 1",
            "ti": "M_SP_NA_1",
            "ioa": "1",
            "scale": "1",
            "unit": "A",
            "default": "0",
            "description": "Test",
        }
    ]
    response = await client.post(
        "/signallisten/import",
        data={"format": "json", "payload": json.dumps(payload)},
        follow_redirects=False,
    )
    assert response.status_code == 302
    export_response = await client.get("/signallisten/export?format=json")
    assert export_response.status_code == 200
    exported = json.loads(export_response.get_data(as_text=True))
    assert exported[0]["name"] == "Signal 1"
