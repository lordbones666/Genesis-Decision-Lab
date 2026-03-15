from __future__ import annotations

from forecasting_engine.simulation.contracts import SimulationContext, SimulationOutput


def bounded(value: float, floor: float = 0.0, ceiling: float = 1.0) -> float:
    return min(max(value, floor), ceiling)


def build_output(
    simulator: str,
    context: SimulationContext,
    state: dict[str, float],
    metrics: dict[str, float],
    assumptions: list[str],
) -> SimulationOutput:
    return SimulationOutput(
        simulator=simulator,
        context=context,
        state=state,
        metrics=metrics,
        assumptions=assumptions,
    )
