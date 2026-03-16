from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScenarioConfidence:
    confidence_level: float
    uncertainty_note: str


@dataclass(frozen=True)
class ScenarioDefinition:
    scenario_id: str
    label: str
    horizon_steps: int
    trigger_set: tuple[str, ...]
    linked_evidence_ids: tuple[str, ...]
    state_assumptions: dict[str, float]
    simulator_targets: tuple[str, ...]
    regime_assumptions: dict[str, float]
    confidence: ScenarioConfidence
    config_version: str
    template_version: str
    metadata: dict[str, str] = field(default_factory=dict)


def validate_scenario(scenario: ScenarioDefinition) -> None:
    if not scenario.scenario_id:
        raise ValueError("scenario_id is required")
    if scenario.horizon_steps <= 0:
        raise ValueError("horizon_steps must be positive")
    if not scenario.trigger_set:
        raise ValueError("trigger_set must include at least one trigger")
    if not scenario.linked_evidence_ids:
        raise ValueError("linked_evidence_ids must include at least one id")
    if not scenario.simulator_targets:
        raise ValueError("simulator_targets must include at least one simulator")
    if not 0.0 <= scenario.confidence.confidence_level <= 1.0:
        raise ValueError("confidence.confidence_level must be in [0, 1]")
