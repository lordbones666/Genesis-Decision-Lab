from __future__ import annotations

from forecasting_engine.simulation.contracts import (
    DomainSimulator,
    SimulationContext,
    SimulationOutput,
)
from forecasting_engine.simulation.domains._shared import bounded, build_output


class AllianceDeterrenceSimulator(DomainSimulator):
    name = "alliance_deterrence"

    def simulate(self, context: SimulationContext, inputs: dict[str, float]) -> SimulationOutput:
        cohesion = bounded(inputs.get("alliance_cohesion", 0.6))
        capability = bounded(inputs.get("capability_readiness", 0.6))
        adversary_risk_tolerance = bounded(inputs.get("adversary_risk_tolerance", 0.5))
        deterrence_score = bounded(0.5 * cohesion + 0.5 * capability)
        escalation_risk = bounded(adversary_risk_tolerance * (1.0 - deterrence_score))
        return build_output(
            simulator=self.name,
            context=context,
            state={"deterrence_score": deterrence_score},
            metrics={"escalation_risk": escalation_risk},
            assumptions=["Deterrence as cohesion+capability blend"],
        )
