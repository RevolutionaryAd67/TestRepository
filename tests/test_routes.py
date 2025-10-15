from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_routes(client) -> None:
    for path in ["/", "/pruefung/", "/signallisten/", "/admin/"]:
        response = await client.get(path)
        assert response.status_code == 200
