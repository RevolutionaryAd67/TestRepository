
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.signale import SignalListEntry, get_engine, init_db


@pytest.mark.asyncio
async def test_signallist_persistence(tmp_path, monkeypatch):
    db_path = tmp_path / "signals.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    await init_db(f"sqlite+aiosqlite:///{db_path}")
    engine = get_engine()
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        entry = SignalListEntry(
            name="Test",
            ti=1,
            ioa=100,
            scale=1.0,
            unit="A",
            default="0",
            description="Demo",
        )
        session.add(entry)
        await session.commit()

    async with sessionmaker() as session:
        result = await session.execute(select(SignalListEntry))
        entries = result.scalars().all()
        assert entries
        assert entries[0].name == "Test"
