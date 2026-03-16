from __future__ import annotations

from forecasting_engine.simulation.contracts import (
    DomainSimulator,
    SimulationContext,
    SimulationOutput,
)
from forecasting_engine.simulation.domains._shared import bounded, build_output


class SocialContagionSimulator(DomainSimulator):
    name = "social_contagion"

    def simulate(self, context: SimulationContext, inputs: dict[str, float]) -> SimulationOutput:
        reproduction_rate = max(inputs.get("narrative_r", 1.1), 0.0)
        moderation_strength = bounded(inputs.get("moderation_strength", 0.35))
        exposure = bounded(inputs.get("exposure", 0.5))
        effective_r = reproduction_rate * (1.0 - 0.5 * moderation_strength)
        spread_risk = bounded((effective_r - 1.0) * exposure)
        return build_output(
            simulator=self.name,
            context=context,
            state={"effective_r": effective_r},
            metrics={"spread_risk": spread_risk},
            assumptions=["Narrative spread uses epidemic-style effective reproduction rate"],
        )
