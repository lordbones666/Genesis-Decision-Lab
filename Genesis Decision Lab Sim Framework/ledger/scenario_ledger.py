from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from forecasting_engine.ledger import JsonlLedger
from forecasting_engine.scenario.contracts import ScenarioDefinition


class ScenarioLedger(JsonlLedger):
    def __init__(self, path: Path) -> None:
        super().__init__(path)

    def append_scenario(self, scenario: ScenarioDefinition) -> None:
        self.append(asdict(scenario))
