"""Predefined IEC-104 test scenarios."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from iec104 import C_SC_NA_1, M_SP_NA_1


@dataclass(slots=True)
class ScenarioStep:
    name: str
    description: str
    payload: object


@dataclass(slots=True)
class Scenario:
    name: str
    steps: List[ScenarioStep]


DEFAULT_SCENARIOS: List[Scenario] = [
    Scenario(
        name="Single Point Toggle",
        steps=[
            ScenarioStep(
                name="Send M_SP_NA_1",
                description="Sends a single point information ASDU",
                payload=M_SP_NA_1(address=1, value=True),
            ),
            ScenarioStep(
                name="Command C_SC_NA_1",
                description="Controls single command to toggle output",
                payload=C_SC_NA_1(address=1, command=True),
            ),
        ],
    )
]


__all__ = ["Scenario", "ScenarioStep", "DEFAULT_SCENARIOS"]
