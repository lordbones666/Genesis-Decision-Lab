from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from typing import Any, Callable

from forecasting_engine.orchestration.contracts import WorldModelRequest, WorldModelResult
from forecasting_engine.orchestration.tool_manifest import (
    SelfModelManifest,
    load_self_model_manifest,
)
from forecasting_engine.orchestration.uncertainty_router import (
    UncertaintyRoutingInput,
    policy_from_dict,
    route_uncertainty,
)
from forecasting_engine.simulation.contracts import BayesianEvidence, SimulationContext
from forecasting_engine.simulation.core.bayesian import bayesian_update
from forecasting_engine.simulation.core.monte_carlo import MonteCarloConfig, run_paths
from forecasting_engine.simulation.core.orchestrator import SimulationOrchestrator

BRIDGE_MANIFEST_PATH = "config/self_model_manifest.yaml"


class WorldModelBridge:
    """Thin adapter exposing existing simulation/predictive modules with one contract."""

    def __init__(
        self,
        orchestrator: SimulationOrchestrator | None = None,
        manifest: SelfModelManifest | None = None,
    ) -> None:
        self._orchestrator = orchestrator or SimulationOrchestrator()
        self._manifest = manifest or load_self_model_manifest(BRIDGE_MANIFEST_PATH)
        self._handlers: dict[str, Callable[[WorldModelRequest], WorldModelResult]] = {
            "bayesian_update": self._call_bayesian_update,
            "monte_carlo_paths": self._call_monte_carlo,
            "domain_simulation": self._call_domain_simulation,
        }

    def call(self, request: WorldModelRequest) -> WorldModelResult:
        if request.tool_name not in self._manifest.tools:
            return self._failure_result(
                request=request,
                reason=f"tool_not_in_manifest:{request.tool_name}",
            )

        handler = self._handlers.get(request.tool_name)
        if handler is None:
            return self._failure_result(
                request=request,
                reason=f"unsupported_tool_handler:{request.tool_name}",
            )

        required_inputs = self._manifest.tools[request.tool_name].required_inputs
        missing = [field for field in required_inputs if field not in request.payload]
        if missing:
            return self._failure_result(
                request=request,
                reason=f"missing_required_inputs:{','.join(sorted(missing))}",
            )
        return handler(request)

    def _call_bayesian_update(self, request: WorldModelRequest) -> WorldModelResult:
        prior = float(request.payload["prior"])
        evidence: list[BayesianEvidence] = []
        for item in request.payload.get("evidence", []):
            evidence.append(
                BayesianEvidence(
                    evidence_id=str(item["evidence_id"]),
                    likelihood_ratio=float(item["likelihood_ratio"]),
                    source_tier=str(item.get("source_tier", "tier2")),
                    weight=float(item.get("weight", 1.0)),
                )
            )
        result = bayesian_update(prior=prior, evidence=evidence, as_of=request.as_of)
        confidence = float(result.confidence_interval[1] - result.confidence_interval[0])
        policy = policy_from_dict(self._manifest.uncertainty_policies[request.tool_name])
        decision = route_uncertainty(
            UncertaintyRoutingInput(
                tool_name=request.tool_name,
                required_inputs=["prior", "evidence"],
                provided_inputs=set(request.payload.keys()),
                confidence=max(0.0, min(1.0, 1.0 - confidence)),
            ),
            policy=policy,
        )
        return WorldModelResult(
            tool_name=request.tool_name,
            summary="Bayesian posterior computed from likelihood-ratio evidence updates.",
            assumptions=["Evidence likelihood ratios are conditionally independent."],
            modeled_variables=["prior", "posterior", "effective_likelihood_ratio"],
            output={
                "prior": result.prior,
                "posterior": result.posterior,
                "effective_likelihood_ratio": result.effective_likelihood_ratio,
                "confidence_interval": list(result.confidence_interval),
                "explanation": result.explanation,
            },
            uncertainty_status=decision.status,
            out_of_domain=decision.status == "out_of_domain",
            traces=_build_trace(
                request=request,
                module="simulation.core.bayesian.bayesian_update",
                manifest_version=self._manifest.version,
                extra={"uncertainty_reasons": decision.reasons},
            ),
            recommended_next_checks=["Validate evidence independence assumptions."],
        )

    def _call_monte_carlo(self, request: WorldModelRequest) -> WorldModelResult:
        cfg = MonteCarloConfig(
            steps=int(request.payload.get("steps", 30)),
            runs=int(request.payload.get("runs", 200)),
            dt=float(request.payload.get("dt", 1.0 / 252.0)),
            jump_probability=float(request.payload.get("jump_probability", 0.0)),
            jump_mean=float(request.payload.get("jump_mean", 0.0)),
            jump_std=float(request.payload.get("jump_std", 0.0)),
        )
        sigma = float(request.payload["sigma"])
        summary, _ = run_paths(
            initial_value=float(request.payload["initial_value"]),
            threshold_value=float(request.payload["threshold_value"]),
            mu=float(request.payload["mu"]),
            sigma=sigma,
            seed=int(request.payload.get("seed", 7)),
            cfg=cfg,
        )
        policy = policy_from_dict(self._manifest.uncertainty_policies[request.tool_name])
        decision = route_uncertainty(
            UncertaintyRoutingInput(
                tool_name=request.tool_name,
                required_inputs=["initial_value", "threshold_value", "mu", "sigma"],
                provided_inputs=set(request.payload.keys()),
                confidence=1.0 - min(max(sigma, 0.0), 1.0),
            ),
            policy=policy,
        )
        return WorldModelResult(
            tool_name=request.tool_name,
            summary="Monte Carlo path simulation completed against threshold target.",
            assumptions=["Returns follow the configured jump-diffusion process."],
            modeled_variables=["threshold_hit_probability", "mean_final_value", "quantiles"],
            output={
                "threshold_hit_probability": summary.threshold_hit_probability,
                "mean_final_value": summary.mean_final_value,
                "quantiles": summary.quantiles,
                "model": summary.model,
                "seed": summary.seed,
            },
            uncertainty_status=decision.status,
            out_of_domain=decision.status == "out_of_domain",
            traces=_build_trace(
                request=request,
                module="simulation.core.monte_carlo.run_paths",
                manifest_version=self._manifest.version,
                extra={
                    "seed": summary.seed,
                    "config_version": "v1",
                    "uncertainty_reasons": decision.reasons,
                },
            ),
            recommended_next_checks=["Stress-test sigma and jump parameters for regime drift."],
        )

    def _call_domain_simulation(self, request: WorldModelRequest) -> WorldModelResult:
        context = SimulationContext(
            scenario_id=str(request.payload.get("scenario_id", "decision-lab-seed")),
            as_of=_parse_dt(request.payload.get("context_as_of"), request.as_of),
            horizon_steps=int(request.payload.get("horizon_steps", 8)),
            seed=int(request.payload.get("seed", 13)),
            config_version=str(request.payload.get("config_version", "v1")),
        )
        simulator_name = str(request.payload["simulator_name"])
        inputs = _coerce_float_mapping(request.payload.get("inputs", {}))
        output = self._orchestrator.run(
            simulator_name=simulator_name, context=context, inputs=inputs
        )

        policy = policy_from_dict(self._manifest.uncertainty_policies[request.tool_name])
        decision = route_uncertainty(
            UncertaintyRoutingInput(
                tool_name=request.tool_name,
                required_inputs=["simulator_name", "inputs"],
                provided_inputs=set(request.payload.keys()),
                confidence=0.7,
                simulator_name=simulator_name,
                variable_names=set(inputs),
            ),
            policy=policy,
        )

        return WorldModelResult(
            tool_name=request.tool_name,
            summary=f"Domain simulation '{simulator_name}' completed.",
            assumptions=output.assumptions,
            modeled_variables=list(output.state.keys()),
            output={
                "simulator": output.simulator,
                "state": output.state,
                "metrics": output.metrics,
                "artifacts": output.artifacts,
                "context": {
                    "scenario_id": output.context.scenario_id,
                    "horizon_steps": output.context.horizon_steps,
                    "seed": output.context.seed,
                    "config_version": output.context.config_version,
                },
            },
            uncertainty_status=decision.status,
            out_of_domain=decision.status == "out_of_domain",
            traces=_build_trace(
                request=request,
                module="simulation.core.orchestrator.SimulationOrchestrator.run",
                manifest_version=self._manifest.version,
                extra={
                    "seed": output.context.seed,
                    "config_version": output.context.config_version,
                    "simulator_name": output.simulator,
                    "uncertainty_reasons": decision.reasons,
                },
            ),
            recommended_next_checks=["Compare against at least one alternative domain simulator."],
        )

    def _failure_result(self, request: WorldModelRequest, reason: str) -> WorldModelResult:
        return WorldModelResult(
            tool_name=request.tool_name,
            summary="World-model call rejected by bridge validation.",
            assumptions=[],
            modeled_variables=[],
            output={},
            uncertainty_status="out_of_domain",
            out_of_domain=True,
            traces=_build_trace(
                request=request,
                module="orchestration.world_model_bridge.validation",
                manifest_version=self._manifest.version,
                extra={"reason": reason},
            ),
            recommended_next_checks=["Review tool name and required payload fields."],
            failure_reason=reason,
        )


def _coerce_float_mapping(raw_inputs: Any) -> dict[str, float]:
    if not isinstance(raw_inputs, dict):
        raise ValueError("domain simulation inputs must be a mapping")
    return {str(key): float(value) for key, value in raw_inputs.items()}


def _parse_dt(value: Any, default: datetime) -> datetime:
    if value is None:
        return default
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def _build_trace(
    request: WorldModelRequest,
    module: str,
    manifest_version: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fingerprint = sha256(
        f"{request.tool_name}|{request.task}|{request.as_of.isoformat()}|{sorted(request.payload.items(), key=str)}".encode(
            "utf-8"
        )
    ).hexdigest()[:16]
    trace: dict[str, Any] = {
        "trace_id": f"wm-{fingerprint}",
        "module": module,
        "tool_name": request.tool_name,
        "as_of": request.as_of.isoformat(),
        "manifest_version": manifest_version,
        "payload_keys": sorted(request.payload.keys()),
    }
    if extra:
        trace.update(extra)
    return trace
