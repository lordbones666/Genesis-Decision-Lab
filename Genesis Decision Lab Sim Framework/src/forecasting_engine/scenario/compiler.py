from __future__ import annotations

import hashlib

from forecasting_engine.scenario.contracts import (
    ScenarioConfidence,
    ScenarioDefinition,
    validate_scenario,
)
from forecasting_engine.scenario.templates import get_template


def _deterministic_scenario_id(template_id: str, label: str, evidence_ids: tuple[str, ...]) -> str:
    key = f"{template_id}|{label}|{'|'.join(sorted(evidence_ids))}"
    return f"scn-{hashlib.sha256(key.encode()).hexdigest()[:16]}"


def compile_scenario(
    *,
    template_id: str,
    label: str,
    linked_evidence_ids: list[str],
    state_assumptions: dict[str, float],
    regime_assumptions: dict[str, float],
    confidence_level: float,
    uncertainty_note: str,
    config_version: str,
    metadata: dict[str, str] | None = None,
) -> ScenarioDefinition:
    template = get_template(template_id)
    evidence_tuple = tuple(sorted(set(linked_evidence_ids)))
    for key in template.required_assumptions:
        if key not in state_assumptions:
            raise ValueError(f"Missing required assumption={key} for template={template_id}")

    scenario = ScenarioDefinition(
        scenario_id=_deterministic_scenario_id(template_id, label, evidence_tuple),
        label=label,
        horizon_steps=template.default_horizon_steps,
        trigger_set=template.default_trigger_set,
        linked_evidence_ids=evidence_tuple,
        state_assumptions=dict(sorted(state_assumptions.items())),
        simulator_targets=template.simulator_targets,
        regime_assumptions=dict(sorted(regime_assumptions.items())),
        confidence=ScenarioConfidence(
            confidence_level=confidence_level,
            uncertainty_note=uncertainty_note,
        ),
        config_version=config_version,
        template_version=template.template_version,
        metadata=metadata or {},
    )
    validate_scenario(scenario)
    return scenario
