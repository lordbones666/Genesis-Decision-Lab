from __future__ import annotations

from forecasting_engine.extensions.regime_detector import detect_regime_vector
from forecasting_engine.simulation.contracts import (
    DomainSimulator,
    SimulationContext,
    SimulationOutput,
)
from forecasting_engine.simulation.domains._shared import bounded, build_output


class MacroSystemSimulator(DomainSimulator):
    name = "macro_system"

    def simulate(self, context: SimulationContext, inputs: dict[str, float]) -> SimulationOutput:
        inflation = inputs.get("inflation", 2.5)
        growth = inputs.get("growth", 2.0)
        unemployment = inputs.get("unemployment", 4.5)
        policy_rate = inputs.get("policy_rate", 4.0)
        shock = inputs.get("shock", 0.0)
        regime = detect_regime_vector(inputs)

        stress = bounded(0.35 * regime.inflation_shock + 0.25 * regime.recession_risk + 0.4 * shock)
        projected_growth = growth - 1.2 * stress + 0.1 * (2.0 - unemployment)
        projected_inflation = inflation + 1.4 * shock - 0.2 * regime.recession_risk
        market_risk_off = bounded(regime.risk_off + 0.3 * stress)

        return build_output(
            simulator=self.name,
            context=context,
            state={"stress": stress, "risk_off": market_risk_off},
            metrics={
                "projected_growth": projected_growth,
                "projected_inflation": projected_inflation,
                "projected_policy_rate": policy_rate + (projected_inflation - 2.0) * 0.4,
            },
            assumptions=["Linearized macro relationships", "Regime vector from existing detector"],
        )
