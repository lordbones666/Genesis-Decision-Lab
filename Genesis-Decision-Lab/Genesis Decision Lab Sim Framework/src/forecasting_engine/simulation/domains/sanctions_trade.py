from __future__ import annotations

from forecasting_engine.simulation.contracts import (
    DomainSimulator,
    SimulationContext,
    SimulationOutput,
)
from forecasting_engine.simulation.domains._shared import bounded, build_output


class SanctionsTradeSimulator(DomainSimulator):
    name = "sanctions_trade"

    def simulate(self, context: SimulationContext, inputs: dict[str, float]) -> SimulationOutput:
        sanction_intensity = bounded(inputs.get("sanction_intensity", 0.2))
        rerouting_capacity = bounded(inputs.get("rerouting_capacity", 0.5))
        compliance_strength = bounded(inputs.get("compliance_strength", 0.7))
        trade_loss = sanction_intensity * compliance_strength * (1.0 - 0.6 * rerouting_capacity)
        leakage = sanction_intensity * (1.0 - compliance_strength)
        return build_output(
            simulator=self.name,
            context=context,
            state={
                "sanction_intensity": sanction_intensity,
                "rerouting_capacity": rerouting_capacity,
            },
            metrics={"trade_loss": trade_loss, "sanction_leakage": leakage},
            assumptions=["Trade-flow reduction with rerouting and compliance controls"],
        )
