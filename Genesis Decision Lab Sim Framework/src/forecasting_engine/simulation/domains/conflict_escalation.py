from __future__ import annotations

from forecasting_engine.simulation.contracts import (
    DomainSimulator,
    SimulationContext,
    SimulationOutput,
)
from forecasting_engine.simulation.core.markov import MarkovChain
from forecasting_engine.simulation.domains._shared import build_output


class ConflictEscalationSimulator(DomainSimulator):
    name = "conflict_escalation"

    def simulate(self, context: SimulationContext, inputs: dict[str, float]) -> SimulationOutput:
        states = ["stable", "escalating", "crisis", "deescalating"]
        escalation_bias = inputs.get("trigger_intensity", 0.2)
        alliance_backstop = inputs.get("alliance_backstop", 0.5)
        matrix = {
            "stable": {
                "stable": 0.78 - 0.2 * escalation_bias,
                "escalating": 0.18 + 0.2 * escalation_bias,
                "crisis": 0.02,
                "deescalating": 0.02,
            },
            "escalating": {
                "stable": 0.12,
                "escalating": 0.54,
                "crisis": 0.28,
                "deescalating": 0.06,
            },
            "crisis": {
                "stable": 0.03,
                "escalating": 0.12,
                "crisis": 0.63 - 0.2 * alliance_backstop,
                "deescalating": 0.22 + 0.2 * alliance_backstop,
            },
            "deescalating": {
                "stable": 0.45,
                "escalating": 0.08,
                "crisis": 0.02,
                "deescalating": 0.45,
            },
        }
        chain = MarkovChain(states=states, transition_matrix=matrix)
        start_state = inputs.get("start_state", "stable")
        state_name = start_state if isinstance(start_state, str) else "stable"
        result = chain.simulate_path(state_name, context.horizon_steps, context.seed)
        crisis_share = result.state_counts["crisis"] / max(context.horizon_steps, 1)
        return build_output(
            simulator=self.name,
            context=context,
            state={key: float(value) for key, value in result.state_counts.items()},
            metrics={"crisis_share": crisis_share, "shipping_spillover_index": 1.5 * crisis_share},
            assumptions=[
                "Finite-state transition model",
                "Alliance backstop dampens crisis persistence",
            ],
        )
