from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioBranch:
    name: str
    probability: float
    assumptions: dict[str, float]


@dataclass(frozen=True)
class ScenarioTree:
    branches: list[ScenarioBranch]


def generate_scenario_tree(
    base_state: dict[str, float],
    uncertainty_drivers: dict[str, float],
    branch_factor: float = 0.2,
) -> ScenarioTree:
    positive_prob = max(0.1, min(0.45, 0.33 + branch_factor / 2.0))
    negative_prob = max(0.1, min(0.45, 0.33 - branch_factor / 3.0))
    neutral_prob = max(0.0, 1.0 - positive_prob - negative_prob)

    bullish = {
        key: value + branch_factor * uncertainty_drivers.get(key, 0.0)
        for key, value in base_state.items()
    }
    neutral = dict(base_state)
    bearish = {
        key: value - branch_factor * uncertainty_drivers.get(key, 0.0)
        for key, value in base_state.items()
    }

    return ScenarioTree(
        branches=[
            ScenarioBranch(name="bullish", probability=positive_prob, assumptions=bullish),
            ScenarioBranch(name="neutral", probability=neutral_prob, assumptions=neutral),
            ScenarioBranch(name="bearish", probability=negative_prob, assumptions=bearish),
        ]
    )
