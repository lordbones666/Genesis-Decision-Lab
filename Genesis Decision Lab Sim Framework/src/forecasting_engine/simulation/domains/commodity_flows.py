from __future__ import annotations

from forecasting_engine.simulation.contracts import (
    DomainSimulator,
    SimulationContext,
    SimulationOutput,
)
from forecasting_engine.simulation.domains._shared import bounded, build_output


class CommodityFlowsSimulator(DomainSimulator):
    name = "commodity_flows"

    def simulate(self, context: SimulationContext, inputs: dict[str, float]) -> SimulationOutput:
        supply_shock = bounded(inputs.get("supply_shock", 0.1))
        demand_shock = bounded(inputs.get("demand_shock", 0.1))
        storage_buffer = bounded(inputs.get("storage_buffer", 0.4))
        net_tightness = bounded(supply_shock + demand_shock - 0.7 * storage_buffer)
        price_index = 1.0 + 2.2 * net_tightness
        return build_output(
            simulator=self.name,
            context=context,
            state={"net_tightness": net_tightness},
            metrics={"commodity_price_index": price_index},
            assumptions=["Single-factor commodity tightness approximation"],
        )
