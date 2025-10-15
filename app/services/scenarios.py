from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class ScenarioStep:
    name: str
    payload: Dict[str, Any]
    delay: float = 0.0


@dataclass(slots=True)
class Scenario:
    name: str
    description: str
    steps: List[ScenarioStep] = field(default_factory=list)

    def add_step(self, step: ScenarioStep) -> None:
        self.steps.append(step)


DEFAULT_SCENARIOS: List[Scenario] = [
    Scenario(
        name="Standard STARTDT",
        description="Performs a STARTDT handshake followed by a TESTFR",
        steps=[
            ScenarioStep(
                name="Send STARTDT",
                payload={"ti": "C_TS_TA_1", "cot": "ACT", "ioa": "0", "values": []},
            ),
            ScenarioStep(
                name="Send TESTFR",
                payload={"ti": "C_TS_TA_1", "cot": "TESTFR", "ioa": "0", "values": []},
                delay=1.0,
            ),
        ],
    )
]


__all__ = ["Scenario", "ScenarioStep", "DEFAULT_SCENARIOS"]
