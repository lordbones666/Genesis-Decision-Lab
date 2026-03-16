from __future__ import annotations

from forecasting_engine.simulation.contracts import (
    DomainSimulator,
    SimulationContext,
    SimulationOutput,
)
from forecasting_engine.simulation.domains._shared import bounded, build_output


class SupplyChainSimulator(DomainSimulator):
    name = "supply_chain"

    def simulate(self, context: SimulationContext, inputs: dict[str, float]) -> SimulationOutput:
        route_disruption = bounded(inputs.get("route_disruption", 0.1))
        inventory_cover = max(inputs.get("inventory_cover_weeks", 6.0), 0.1)
        supplier_concentration = bounded(inputs.get("supplier_concentration", 0.4))
        delay = 2.0 + 12.0 * route_disruption * supplier_concentration / inventory_cover
        price_pressure = bounded(route_disruption * 0.7 + supplier_concentration * 0.2)
        return build_output(
            simulator=self.name,
            context=context,
            state={
                "route_disruption": route_disruption,
                "supplier_concentration": supplier_concentration,
            },
            metrics={"delay_weeks": delay, "price_pressure": price_pressure},
            assumptions=["Simplified network bottleneck model"],
        )
