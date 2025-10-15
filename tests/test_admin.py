from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_admin_update_settings(client) -> None:
    response = await client.post(
        "/admin/settings",
        data={"log_level": "DEBUG", "ringbuffer_size": "20000"},
        follow_redirects=False,
    )
    assert response.status_code == 302
