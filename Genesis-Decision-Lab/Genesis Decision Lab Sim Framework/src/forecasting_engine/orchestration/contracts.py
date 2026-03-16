from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

RoutingDecision = Literal["retrieve", "simulate", "retrieve_and_simulate", "refuse"]
UncertaintyStatus = Literal["valid", "partial", "out_of_domain"]


@dataclass(frozen=True)
class WorldModelRequest:
    tool_name: str
    task: str
    payload: dict[str, Any]
    as_of: datetime


@dataclass(frozen=True)
class WorldModelResult:
    tool_name: str
    summary: str
    assumptions: list[str]
    modeled_variables: list[str]
    output: dict[str, Any]
    uncertainty_status: UncertaintyStatus
    out_of_domain: bool
    traces: dict[str, Any] = field(default_factory=dict)
    recommended_next_checks: list[str] = field(default_factory=list)
    failure_reason: str | None = None


@dataclass(frozen=True)
class OrchestrationResponse:
    task: str
    routing_decision: RoutingDecision
    retrieval_notes: list[str]
    world_model_result: WorldModelResult | None
    known_unknowns: list[str]
    used_manifest_version: str | None = None
