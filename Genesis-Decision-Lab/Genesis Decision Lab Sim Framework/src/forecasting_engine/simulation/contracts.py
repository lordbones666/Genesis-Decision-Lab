from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class SimulationContext:
    scenario_id: str
    as_of: datetime
    horizon_steps: int
    seed: int
    config_version: str


@dataclass(frozen=True)
class BayesianEvidence:
    evidence_id: str
    likelihood_ratio: float
    source_tier: str = "tier2"
    weight: float = 1.0
    observed_at: datetime | None = None


@dataclass(frozen=True)
class BayesianUpdateResult:
    prior: float
    posterior: float
    effective_likelihood_ratio: float
    confidence_interval: tuple[float, float]
    explanation: dict[str, float | str]


@dataclass(frozen=True)
class MarkovStep:
    step: int
    state: str


@dataclass(frozen=True)
class MarkovSimulationResult:
    start_state: str
    path: list[MarkovStep]
    state_counts: dict[str, int]


@dataclass(frozen=True)
class MonteCarloPathResult:
    final_value: float
    hit_threshold: bool
    max_value: float
    min_value: float


@dataclass(frozen=True)
class MonteCarloRunSummary:
    threshold_hit_probability: float
    mean_final_value: float
    quantiles: dict[str, float]
    model: str
    seed: int


@dataclass(frozen=True)
class SimulationOutput:
    simulator: str
    context: SimulationContext
    state: dict[str, float]
    metrics: dict[str, float]
    assumptions: list[str]
    artifacts: dict[str, float | str | dict[str, float]] = field(default_factory=dict)


@dataclass(frozen=True)
class SimulationRunRecord:
    run_id: str
    simulator: str
    simulator_version: str
    scenario_id: str
    as_of: datetime
    seed: int
    config_version: str
    evidence_snapshot_hash: str
    regime_snapshot: dict[str, float]
    output_summary: dict[str, float | str | dict[str, float]]
    failed: bool
    failure_reason: str | None = None


class DomainSimulator(Protocol):
    name: str

    def simulate(
        self, context: SimulationContext, inputs: dict[str, float]
    ) -> SimulationOutput: ...
