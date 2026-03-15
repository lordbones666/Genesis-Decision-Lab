from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from forecasting_engine.orchestration.contracts import UncertaintyStatus


@dataclass(frozen=True)
class UncertaintyRoutingInput:
    tool_name: str
    required_inputs: list[str]
    provided_inputs: set[str]
    confidence: float
    stale_evidence_days: int | None = None
    simulator_name: str | None = None
    variable_names: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class UncertaintyPolicy:
    partial_confidence_min: float = 0.35
    valid_confidence_min: float = 0.60
    stale_evidence_days_max: int | None = 90
    allowed_simulators: set[str] = field(default_factory=set)
    allowed_variables: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class UncertaintyDecision:
    status: UncertaintyStatus
    reasons: list[str]


def policy_from_dict(raw_policy: dict[str, Any]) -> UncertaintyPolicy:
    allowed_simulators = raw_policy.get("allowed_simulators", [])
    allowed_variables = raw_policy.get("allowed_variables", [])

    if not isinstance(allowed_simulators, list) or not all(
        isinstance(item, str) for item in allowed_simulators
    ):
        raise ValueError("uncertainty policy 'allowed_simulators' must be list[str]")
    if not isinstance(allowed_variables, list) or not all(
        isinstance(item, str) for item in allowed_variables
    ):
        raise ValueError("uncertainty policy 'allowed_variables' must be list[str]")

    stale_limit = raw_policy.get("stale_evidence_days_max", 90)
    if stale_limit is not None and not isinstance(stale_limit, int):
        raise ValueError("uncertainty policy 'stale_evidence_days_max' must be int or null")

    return UncertaintyPolicy(
        partial_confidence_min=float(raw_policy.get("partial_confidence_min", 0.35)),
        valid_confidence_min=float(raw_policy.get("valid_confidence_min", 0.60)),
        stale_evidence_days_max=stale_limit,
        allowed_simulators=set(allowed_simulators),
        allowed_variables=set(allowed_variables),
    )


def route_uncertainty(
    signal: UncertaintyRoutingInput, policy: UncertaintyPolicy
) -> UncertaintyDecision:
    reasons: list[str] = []
    missing_inputs = [item for item in signal.required_inputs if item not in signal.provided_inputs]
    if missing_inputs:
        reasons.append(f"missing_inputs:{','.join(sorted(missing_inputs))}")

    stale_evidence = (
        signal.stale_evidence_days is not None
        and policy.stale_evidence_days_max is not None
        and signal.stale_evidence_days > policy.stale_evidence_days_max
    )
    if stale_evidence:
        reasons.append("stale_evidence")

    if signal.simulator_name and policy.allowed_simulators:
        if signal.simulator_name not in policy.allowed_simulators:
            reasons.append(f"unsupported_simulator:{signal.simulator_name}")

    if signal.variable_names and policy.allowed_variables:
        unsupported = signal.variable_names - policy.allowed_variables
        if unsupported:
            reasons.append(f"unsupported_variables:{','.join(sorted(unsupported))}")

    if signal.confidence < policy.partial_confidence_min:
        reasons.append("confidence_below_partial_min")
        return UncertaintyDecision(status="out_of_domain", reasons=reasons)

    if reasons or signal.confidence < policy.valid_confidence_min:
        if signal.confidence < policy.valid_confidence_min:
            reasons.append("confidence_below_valid_min")
        return UncertaintyDecision(status="partial", reasons=reasons)

    return UncertaintyDecision(status="valid", reasons=["meets_policy"])
