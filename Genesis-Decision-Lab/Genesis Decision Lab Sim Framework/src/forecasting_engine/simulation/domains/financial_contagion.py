from __future__ import annotations

from forecasting_engine.extensions.dependency_graph import DependencyEdge, propagate_dependencies
from forecasting_engine.simulation.contracts import (
    DomainSimulator,
    SimulationContext,
    SimulationOutput,
)
from forecasting_engine.simulation.domains._shared import build_output


class FinancialContagionSimulator(DomainSimulator):
    name = "financial_contagion"

    def simulate(self, context: SimulationContext, inputs: dict[str, float]) -> SimulationOutput:
        base = {
            "bank_core": inputs.get("bank_core_stress", 0.2),
            "shadow_banks": inputs.get("shadow_banks_stress", 0.15),
            "funding": 0.2,
            "credit": 0.2,
            "real_economy": 0.2,
        }
        edges = [
            DependencyEdge("bank_core", "funding", 0.7),
            DependencyEdge("bank_core", "credit", 0.6),
            DependencyEdge("shadow_banks", "funding", 0.5),
            DependencyEdge("funding", "credit", 0.5),
            DependencyEdge("credit", "real_economy", 0.65),
        ]
        stressed = propagate_dependencies(
            probabilities=base,
            edges=edges,
            changed_node="bank_core",
            delta=inputs.get("shock_delta", 0.18),
        )
        stressed = propagate_dependencies(
            probabilities=stressed,
            edges=edges,
            changed_node="shadow_banks",
            delta=inputs.get("shadow_shock_delta", 0.1),
        )
        return build_output(
            simulator=self.name,
            context=context,
            state={k: float(v) for k, v in stressed.items()},
            metrics={"systemic_stress": float(stressed.get("real_economy", 0.0))},
            assumptions=["Node-based dependency propagation", "Sequential funding stress updates"],
        )
