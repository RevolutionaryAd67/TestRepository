"""SQLAlchemy models for signal lists."""
from __future__ import annotations

from typing import Optional

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

_ENGINE: AsyncEngine | None = None


class Base(DeclarativeBase):
    """Declarative base for SQLAlchemy models."""


class SignalListEntry(Base):
    """Represents a single IEC-104 signal list entry."""

    __tablename__ = "signal_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ti: Mapped[int] = mapped_column(Integer, nullable=False)
    ioa: Mapped[int] = mapped_column(Integer, nullable=False)
    scale: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    default: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


async def init_db(database_url: str) -> None:
    """Initialise the SQLite database."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_async_engine(database_url, future=True, echo=False)
        async with _ENGINE.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


def get_engine() -> AsyncEngine:
    """Return the initialised async engine."""
    if _ENGINE is None:  # pragma: no cover - guarded by Quart lifecycle
        raise RuntimeError("Database engine not initialised. Call init_db() first.")
    return _ENGINE
