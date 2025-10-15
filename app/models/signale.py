from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from sqlalchemy import Integer, MetaData, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData()


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    ti: Mapped[str] = mapped_column(String(20), nullable=False)
    ioa: Mapped[str] = mapped_column(String(20), nullable=False)
    scale: Mapped[str] = mapped_column(String(20), nullable=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=True)
    default: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    def to_dict(self) -> dict[str, str | None]:
        return {
            "id": str(self.id),
            "name": self.name,
            "ti": self.ti,
            "ioa": self.ioa,
            "scale": self.scale,
            "unit": self.unit,
            "default": self.default,
            "description": self.description,
        }


@dataclass
class SignalRecord:
    name: str
    ti: str
    ioa: str
    scale: str | None = None
    unit: str | None = None
    default: str | None = None
    description: str | None = None


class SignalRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_signals(self) -> List[Signal]:
        return list(self.session.query(Signal).order_by(Signal.name))

    def upsert(self, records: Iterable[SignalRecord]) -> None:
        for record in records:
            signal = (
                self.session.query(Signal)
                .filter(Signal.name == record.name, Signal.ioa == record.ioa)
                .one_or_none()
            )
            if signal:
                signal.ti = record.ti
                signal.scale = record.scale
                signal.unit = record.unit
                signal.default = record.default
                signal.description = record.description
            else:
                signal = Signal(
                    name=record.name,
                    ti=record.ti,
                    ioa=record.ioa,
                    scale=record.scale,
                    unit=record.unit,
                    default=record.default,
                    description=record.description,
                )
                self.session.add(signal)
        self.session.commit()

    def delete_all(self) -> None:
        self.session.query(Signal).delete()
        self.session.commit()

    def export(self) -> List[dict[str, str | None]]:
        return [signal.to_dict() for signal in self.list_signals()]

    def import_records(self, records: Sequence[dict[str, str | None]]) -> None:
        signal_records = [
            SignalRecord(
                name=record.get("name", ""),
                ti=record.get("ti", ""),
                ioa=record.get("ioa", ""),
                scale=record.get("scale"),
                unit=record.get("unit"),
                default=record.get("default"),
                description=record.get("description"),
            )
            for record in records
        ]
        self.upsert(signal_records)


__all__ = ["Signal", "SignalRepository", "SignalRecord", "Base"]
