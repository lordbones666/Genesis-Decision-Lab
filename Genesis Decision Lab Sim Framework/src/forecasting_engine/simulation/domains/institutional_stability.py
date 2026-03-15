from __future__ import annotations

from forecasting_engine.simulation.contracts import (
    DomainSimulator,
    SimulationContext,
    SimulationOutput,
)
from forecasting_engine.simulation.domains._shared import bounded, build_output


class InstitutionalStabilitySimulator(DomainSimulator):
    name = "institutional_stability"

    def simulate(self, context: SimulationContext, inputs: dict[str, float]) -> SimulationOutput:
        governance_quality = bounded(inputs.get("governance_quality", 0.55))
        fiscal_space = bounded(inputs.get("fiscal_space", 0.45))
        polarization = bounded(inputs.get("polarization", 0.5))
        stability = bounded(0.5 * governance_quality + 0.3 * fiscal_space - 0.4 * polarization)
        failure_risk = bounded(1.0 - stability)
        return build_output(
            simulator=self.name,
            context=context,
            state={"stability": stability},
            metrics={"institutional_failure_risk": failure_risk},
            assumptions=["Reduced-form institutional resilience model"],
        )
