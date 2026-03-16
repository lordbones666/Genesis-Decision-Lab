from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioTemplate:
    template_id: str
    template_version: str
    label: str
    default_horizon_steps: int
    default_trigger_set: tuple[str, ...]
    required_assumptions: tuple[str, ...]
    simulator_targets: tuple[str, ...]


DEFAULT_TEMPLATES: dict[str, ScenarioTemplate] = {
    "macro_stress": ScenarioTemplate(
        template_id="macro_stress",
        template_version="v1",
        label="Macro Stress",
        default_horizon_steps=12,
        default_trigger_set=("inflation_shock", "credit_spread_widening"),
        required_assumptions=("inflation", "growth", "policy_rate"),
        simulator_targets=("macro_system", "financial_contagion"),
    ),
    "conflict_spillover": ScenarioTemplate(
        template_id="conflict_spillover",
        template_version="v1",
        label="Conflict Spillover",
        default_horizon_steps=10,
        default_trigger_set=("border_incident", "alliance_mobilization"),
        required_assumptions=("trigger_intensity", "deterrence_strength"),
        simulator_targets=("conflict_escalation", "alliance_deterrence", "supply_chain"),
    ),
}


def get_template(template_id: str) -> ScenarioTemplate:
    if template_id not in DEFAULT_TEMPLATES:
        raise KeyError(f"Unknown template_id={template_id}")
    return DEFAULT_TEMPLATES[template_id]
