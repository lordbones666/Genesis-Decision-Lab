from __future__ import annotations

from forecasting_engine.scenario.contracts import ScenarioDefinition


class ScenarioRegistry:
    def __init__(self) -> None:
        self._scenarios: dict[str, ScenarioDefinition] = {}

    def register(self, scenario: ScenarioDefinition) -> None:
        self._scenarios[scenario.scenario_id] = scenario

    def get(self, scenario_id: str) -> ScenarioDefinition:
        if scenario_id not in self._scenarios:
            raise KeyError(f"Unknown scenario_id={scenario_id}")
        return self._scenarios[scenario_id]

    def list_ids(self) -> list[str]:
        return sorted(self._scenarios)
