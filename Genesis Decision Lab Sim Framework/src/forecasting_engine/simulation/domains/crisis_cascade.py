from __future__ import annotations

from forecasting_engine.extensions.event_network import propagate_event_shock
from forecasting_engine.simulation.contracts import (
    DomainSimulator,
    SimulationContext,
    SimulationOutput,
)
from forecasting_engine.simulation.domains._shared import build_output


class CrisisCascadeSimulator(DomainSimulator):
    name = "crisis_cascade"

    def simulate(self, context: SimulationContext, inputs: dict[str, float]) -> SimulationOutput:
        edges = [
            ("conflict", "shipping", 0.5),
            ("conflict", "energy", 0.55),
            ("shipping", "inflation", 0.35),
            ("energy", "inflation", 0.45),
            ("energy", "growth", -0.3),
        ]
        base_probabilities = {
            "conflict": 0.4,
            "shipping": 0.4,
            "energy": 0.4,
            "inflation": 0.4,
            "growth": 0.6,
        }
        impact = propagate_event_shock(
            base_probabilities=base_probabilities,
            edges=edges,
            shocked_event="conflict",
            shock_delta=inputs.get("conflict_shock", 0.2),
            max_depth=3,
        )
        inflation_pressure = max(
            impact.get("inflation", 0.0) - base_probabilities["inflation"], 0.0
        )
        return build_output(
            simulator=self.name,
            context=context,
            state={k: float(v) for k, v in impact.items()},
            metrics={"inflation_pressure": inflation_pressure},
            assumptions=["Event-network propagation from existing extension"],
        )
