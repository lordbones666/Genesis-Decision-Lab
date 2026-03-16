from __future__ import annotations

from forecasting_engine.simulation.contracts import SimulationContext, SimulationOutput
from forecasting_engine.simulation.registry import SimulationRegistry, build_default_registry


class SimulationOrchestrator:
    def __init__(self, registry: SimulationRegistry | None = None) -> None:
        self.registry = registry or build_default_registry()

    def run(
        self, simulator_name: str, context: SimulationContext, inputs: dict[str, float]
    ) -> SimulationOutput:
        simulator = self.registry.get(simulator_name)
        return simulator.simulate(context, inputs)
