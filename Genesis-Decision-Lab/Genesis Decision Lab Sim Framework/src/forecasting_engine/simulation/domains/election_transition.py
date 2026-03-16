from __future__ import annotations

from forecasting_engine.simulation.contracts import (
    DomainSimulator,
    SimulationContext,
    SimulationOutput,
)
from forecasting_engine.simulation.domains._shared import bounded, build_output


class ElectionTransitionSimulator(DomainSimulator):
    name = "election_transition"

    def simulate(self, context: SimulationContext, inputs: dict[str, float]) -> SimulationOutput:
        incumbent_popularity = bounded(inputs.get("incumbent_popularity", 0.5))
        institutional_trust = bounded(inputs.get("institutional_trust", 0.5))
        misinformation = bounded(inputs.get("misinformation", 0.3))
        transition_stability = bounded(
            0.6 * institutional_trust + 0.4 * incumbent_popularity - 0.3 * misinformation
        )
        contestation_risk = bounded(1.0 - transition_stability)
        return build_output(
            simulator=self.name,
            context=context,
            state={"transition_stability": transition_stability},
            metrics={"post_election_contestation_risk": contestation_risk},
            assumptions=["Transition risk shaped by trust, popularity, and misinformation"],
        )
