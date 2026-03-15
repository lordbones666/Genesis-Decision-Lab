from __future__ import annotations

from forecasting_engine.simulation.contracts import (
    DomainSimulator,
    SimulationContext,
    SimulationOutput,
)
from forecasting_engine.simulation.domains._shared import bounded, build_output


class MigrationUnrestSimulator(DomainSimulator):
    name = "migration_unrest"

    def simulate(self, context: SimulationContext, inputs: dict[str, float]) -> SimulationOutput:
        displacement = bounded(inputs.get("displacement_pressure", 0.3))
        labor_absorption = bounded(inputs.get("labor_absorption", 0.4))
        public_services = bounded(inputs.get("public_service_capacity", 0.5))
        unrest_risk = bounded(displacement * (1.0 - 0.5 * labor_absorption - 0.3 * public_services))
        return build_output(
            simulator=self.name,
            context=context,
            state={"displacement": displacement},
            metrics={"unrest_risk": unrest_risk, "migration_flow_index": displacement * 1.6},
            assumptions=["Migration pressure tempered by absorption and services"],
        )
