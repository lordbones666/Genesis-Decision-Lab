from __future__ import annotations

from datetime import datetime
from typing import Any

from forecasting_engine.orchestration.contracts import (
    OrchestrationResponse,
    RoutingDecision,
    WorldModelRequest,
)
from forecasting_engine.orchestration.tool_manifest import load_self_model_manifest
from forecasting_engine.orchestration.world_model_bridge import WorldModelBridge

MANIFEST_PATH = "config/self_model_manifest.yaml"


def run_decision_lab_task(
    task_text: str,
    payload: dict[str, Any],
    as_of: datetime,
) -> OrchestrationResponse:
    manifest = load_self_model_manifest(MANIFEST_PATH)
    routing_decision, selected_tool = _classify_and_route(
        task_text, payload, manifest.routing_defaults
    )

    if selected_tool is None:
        return OrchestrationResponse(
            task=task_text,
            routing_decision=routing_decision,
            retrieval_notes=[],
            world_model_result=None,
            known_unknowns=["Task does not map to a configured world-model tool."],
            used_manifest_version=manifest.version,
        )

    bridge = WorldModelBridge(manifest=manifest)
    result = bridge.call(
        WorldModelRequest(
            tool_name=selected_tool,
            task=task_text,
            payload=payload,
            as_of=as_of,
        )
    )
    return OrchestrationResponse(
        task=task_text,
        routing_decision=routing_decision,
        retrieval_notes=[],
        world_model_result=result,
        known_unknowns=(
            [] if not result.out_of_domain else ["Bridge marked result as out_of_domain."]
        ),
        used_manifest_version=manifest.version,
    )


def _classify_and_route(
    task_text: str,
    payload: dict[str, Any],
    routing_defaults: dict[str, Any],
) -> tuple[RoutingDecision, str | None]:
    lowered = task_text.lower()
    if "posterior" in lowered or "bayes" in lowered:
        return "simulate", "bayesian_update"
    if "monte" in lowered or "threshold" in lowered or "volatility" in lowered:
        return "simulate", "monte_carlo_paths"
    if "hidden state" in lowered or "latent" in lowered:
        return "simulate", "hidden_state_estimator"
    if "uncertainty" in lowered and "decomposition" in lowered:
        return "simulate", "uncertainty_decomposition"
    if "value of information" in lowered or "voi" in lowered:
        return "simulate", "value_of_information"
    if "arbitration" in lowered or "disagreement" in lowered or "ensemble" in lowered:
        return "simulate", "model_arbitration"
    if "causal" in lowered or "intervention" in lowered:
        return "simulate", "structural_causal_graph"
    if "contagion" in lowered or "cascade" in lowered or "network" in lowered:
        return "simulate", "network_contagion"
    if "actor" in lowered or "strategic" in lowered:
        return "simulate", "actor_response"
    if "hazard" in lowered or "failure" in lowered or "survival" in lowered:
        return "simulate", "hazard_failure"
    if "scenario tree" in lowered or "branches" in lowered:
        return "simulate", "scenario_tree_generator"
    if "simulate" in lowered or "scenario" in lowered or "domain" in lowered:
        return "simulate", "domain_simulation"

    key_set = set(payload)
    if "simulator_name" in payload and "inputs" in payload:
        return "simulate", "domain_simulation"
    if {"indicators"} <= key_set:
        return "simulate", "hidden_state_estimator"
    if {"sensitivities", "parameter_uncertainty"} <= key_set:
        return "simulate", "uncertainty_decomposition"
    if {"action_gap", "uncertainty_weights", "information_gain"} <= key_set:
        return "simulate", "value_of_information"
    if {"model_outputs"} <= key_set:
        return "simulate", "model_arbitration"
    if {"baseline", "edges", "intervention_node", "intervention_delta"} <= key_set:
        return "simulate", "structural_causal_graph"
    if {"node_states", "edges", "trigger_node", "trigger_delta"} <= key_set:
        return "simulate", "network_contagion"
    if {"actors", "trigger_intensity"} <= key_set:
        return "simulate", "actor_response"
    if {"stress_level", "vulnerability", "horizon"} <= key_set:
        return "simulate", "hazard_failure"
    if {"base_state", "uncertainty_drivers"} <= key_set:
        return "simulate", "scenario_tree_generator"

    unsupported_action = routing_defaults.get("unsupported_task_action", "refuse")
    if unsupported_action in {"retrieve", "simulate", "retrieve_and_simulate", "refuse"}:
        return unsupported_action, None
    return "refuse", None
