from __future__ import annotations

from forecasting_engine.simulation.contracts import DomainSimulator
from forecasting_engine.simulation.domains.alliance_deterrence import AllianceDeterrenceSimulator
from forecasting_engine.simulation.domains.commodity_flows import CommodityFlowsSimulator
from forecasting_engine.simulation.domains.conflict_escalation import ConflictEscalationSimulator
from forecasting_engine.simulation.domains.crisis_cascade import CrisisCascadeSimulator
from forecasting_engine.simulation.domains.election_transition import ElectionTransitionSimulator
from forecasting_engine.simulation.domains.financial_contagion import FinancialContagionSimulator
from forecasting_engine.simulation.domains.institutional_stability import (
    InstitutionalStabilitySimulator,
)
from forecasting_engine.simulation.domains.macro_system import MacroSystemSimulator
from forecasting_engine.simulation.domains.migration_unrest import MigrationUnrestSimulator
from forecasting_engine.simulation.domains.sanctions_trade import SanctionsTradeSimulator
from forecasting_engine.simulation.domains.social_contagion import SocialContagionSimulator
from forecasting_engine.simulation.domains.supply_chain import SupplyChainSimulator


class SimulationRegistry:
    def __init__(self) -> None:
        self._simulators: dict[str, DomainSimulator] = {}

    def register(self, simulator: DomainSimulator) -> None:
        self._simulators[simulator.name] = simulator

    def get(self, name: str) -> DomainSimulator:
        if name not in self._simulators:
            raise KeyError(f"Unknown simulator={name}")
        return self._simulators[name]

    def names(self) -> list[str]:
        return sorted(self._simulators)


def build_default_registry() -> SimulationRegistry:
    registry = SimulationRegistry()
    for simulator in [
        MacroSystemSimulator(),
        ConflictEscalationSimulator(),
        CrisisCascadeSimulator(),
        FinancialContagionSimulator(),
        SupplyChainSimulator(),
        SanctionsTradeSimulator(),
        CommodityFlowsSimulator(),
        AllianceDeterrenceSimulator(),
        InstitutionalStabilitySimulator(),
        MigrationUnrestSimulator(),
        ElectionTransitionSimulator(),
        SocialContagionSimulator(),
    ]:
        registry.register(simulator)
    return registry
