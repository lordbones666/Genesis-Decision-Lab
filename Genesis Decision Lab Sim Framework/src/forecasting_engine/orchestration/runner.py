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
    if "simulate" in lowered or "scenario" in lowered or "domain" in lowered:
        return "simulate", "domain_simulation"

    if "simulator_name" in payload and "inputs" in payload:
        return "simulate", "domain_simulation"

    unsupported_action = routing_defaults.get("unsupported_task_action", "refuse")
    if unsupported_action in {"retrieve", "simulate", "retrieve_and_simulate", "refuse"}:
        return unsupported_action, None
    return "refuse", None
