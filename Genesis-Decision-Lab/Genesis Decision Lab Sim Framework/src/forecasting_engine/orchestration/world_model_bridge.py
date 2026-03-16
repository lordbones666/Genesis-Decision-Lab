from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from typing import Any, Callable

from forecasting_engine.extensions.actor_response import ActorProfile, simulate_actor_response
from forecasting_engine.extensions.hazard_failure import estimate_hazard_failure
from forecasting_engine.extensions.hidden_state_estimator import estimate_hidden_state
from forecasting_engine.extensions.model_arbitration import arbitrate_models
from forecasting_engine.extensions.network_contagion import NetworkEdge, propagate_contagion
from forecasting_engine.extensions.scenario_tree_generator import generate_scenario_tree
from forecasting_engine.extensions.structural_causal_graph import (
    CausalEdge,
    run_structural_causal_graph,
)
from forecasting_engine.extensions.uncertainty_decomposition import decompose_uncertainty
from forecasting_engine.extensions.value_of_information import value_of_information
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
            "structural_causal_graph": self._call_structural_causal_graph,
            "network_contagion": self._call_network_contagion,
            "actor_response": self._call_actor_response,
            "hazard_failure": self._call_hazard_failure,
            "scenario_tree_generator": self._call_scenario_tree_generator,
            "hidden_state_estimator": self._call_hidden_state_estimator,
            "uncertainty_decomposition": self._call_uncertainty_decomposition,
            "value_of_information": self._call_value_of_information,
            "model_arbitration": self._call_model_arbitration,
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

    def _call_structural_causal_graph(self, request: WorldModelRequest) -> WorldModelResult:
        baseline = _coerce_float_mapping(request.payload["baseline"])
        edges = [
            CausalEdge(str(item["parent"]), str(item["child"]), float(item["weight"]))
            for item in request.payload.get("edges", [])
        ]
        result = run_structural_causal_graph(
            baseline=baseline,
            edges=edges,
            intervention_node=str(request.payload["intervention_node"]),
            intervention_delta=float(request.payload["intervention_delta"]),
            steps=int(request.payload.get("steps", 2)),
        )
        policy = policy_from_dict(self._manifest.uncertainty_policies[request.tool_name])
        decision = route_uncertainty(
            UncertaintyRoutingInput(
                tool_name=request.tool_name,
                required_inputs=["baseline", "edges", "intervention_node", "intervention_delta"],
                provided_inputs=set(request.payload.keys()),
                confidence=0.68,
                variable_names=set(baseline),
            ),
            policy=policy,
        )
        return WorldModelResult(
            tool_name=request.tool_name,
            summary="Structural causal propagation computed for intervention scenario.",
            assumptions=["Edge weights approximate local structural influence."],
            modeled_variables=list(result.downstream_effects.keys()),
            output={
                "downstream_effects": result.downstream_effects,
                "intervention_forecast": result.intervention_forecast,
                "causal_sensitivity": result.causal_sensitivity,
            },
            uncertainty_status=decision.status,
            out_of_domain=decision.status == "out_of_domain",
            traces=_build_trace(
                request=request,
                module="extensions.structural_causal_graph.run_structural_causal_graph",
                manifest_version=self._manifest.version,
                extra={"uncertainty_reasons": decision.reasons},
            ),
            recommended_next_checks=["Validate edge directionality and intervention assumptions."],
        )

    def _call_network_contagion(self, request: WorldModelRequest) -> WorldModelResult:
        nodes = _coerce_float_mapping(request.payload["node_states"])
        edges = [
            NetworkEdge(str(item["source"]), str(item["target"]), float(item["weight"]))
            for item in request.payload.get("edges", [])
        ]
        result = propagate_contagion(
            node_states=nodes,
            edges=edges,
            trigger_node=str(request.payload["trigger_node"]),
            trigger_delta=float(request.payload["trigger_delta"]),
            threshold=float(request.payload.get("threshold", 0.55)),
            iterations=int(request.payload.get("iterations", 3)),
        )
        policy = policy_from_dict(self._manifest.uncertainty_policies[request.tool_name])
        decision = route_uncertainty(
            UncertaintyRoutingInput(
                tool_name=request.tool_name,
                required_inputs=["node_states", "edges", "trigger_node", "trigger_delta"],
                provided_inputs=set(request.payload.keys()),
                confidence=0.66,
                variable_names=set(nodes),
            ),
            policy=policy,
        )
        return WorldModelResult(
            tool_name=request.tool_name,
            summary="Network contagion propagation completed.",
            assumptions=["Edge weights represent transmissible dependency strength."],
            modeled_variables=list(result.node_states.keys()),
            output={
                "node_states": result.node_states,
                "cascade_likelihood": result.cascade_likelihood,
                "critical_nodes": result.critical_nodes,
            },
            uncertainty_status=decision.status,
            out_of_domain=decision.status == "out_of_domain",
            traces=_build_trace(
                request=request,
                module="extensions.network_contagion.propagate_contagion",
                manifest_version=self._manifest.version,
                extra={"uncertainty_reasons": decision.reasons},
            ),
            recommended_next_checks=["Stress edge weights and threshold for cascade stability."],
        )

    def _call_actor_response(self, request: WorldModelRequest) -> WorldModelResult:
        actors = [
            ActorProfile(
                name=str(item["name"]),
                incentive=float(item["incentive"]),
                constraint=float(item["constraint"]),
                risk_tolerance=float(item["risk_tolerance"]),
            )
            for item in request.payload.get("actors", [])
        ]
        result = simulate_actor_response(
            actors=actors,
            trigger_intensity=float(request.payload["trigger_intensity"]),
            policy_pressure=float(request.payload.get("policy_pressure", 0.0)),
        )
        policy = policy_from_dict(self._manifest.uncertainty_policies[request.tool_name])
        decision = route_uncertainty(
            UncertaintyRoutingInput(
                tool_name=request.tool_name,
                required_inputs=["actors", "trigger_intensity"],
                provided_inputs=set(request.payload.keys()),
                confidence=0.62,
            ),
            policy=policy,
        )
        return WorldModelResult(
            tool_name=request.tool_name,
            summary="Actor-response branches and action probabilities estimated.",
            assumptions=["Actor utility is approximated with bounded-rational weighting."],
            modeled_variables=list(result.action_probabilities.keys()),
            output={
                "action_probabilities": result.action_probabilities,
                "strategic_branches": result.strategic_branches,
                "adversarial_risk": result.adversarial_risk,
            },
            uncertainty_status=decision.status,
            out_of_domain=decision.status == "out_of_domain",
            traces=_build_trace(
                request=request,
                module="extensions.actor_response.simulate_actor_response",
                manifest_version=self._manifest.version,
                extra={"uncertainty_reasons": decision.reasons},
            ),
            recommended_next_checks=[
                "Cross-check actor priors against alternative incentive assumptions."
            ],
        )

    def _call_hazard_failure(self, request: WorldModelRequest) -> WorldModelResult:
        result = estimate_hazard_failure(
            stress_level=float(request.payload["stress_level"]),
            vulnerability=float(request.payload["vulnerability"]),
            horizon=float(request.payload["horizon"]),
            baseline_hazard=float(request.payload.get("baseline_hazard", 0.03)),
        )
        policy = policy_from_dict(self._manifest.uncertainty_policies[request.tool_name])
        decision = route_uncertainty(
            UncertaintyRoutingInput(
                tool_name=request.tool_name,
                required_inputs=["stress_level", "vulnerability", "horizon"],
                provided_inputs=set(request.payload.keys()),
                confidence=max(0.0, min(1.0, 1.0 - min(result.hazard_rate, 1.0))),
            ),
            policy=policy,
        )
        return WorldModelResult(
            tool_name=request.tool_name,
            summary="Hazard and failure probability estimated for specified horizon.",
            assumptions=["Hazard rate is stationary over the supplied horizon."],
            modeled_variables=["hazard_rate", "survival_probability", "event_probability"],
            output={
                "hazard_rate": result.hazard_rate,
                "survival_probability": result.survival_probability,
                "event_probability": result.event_probability,
            },
            uncertainty_status=decision.status,
            out_of_domain=decision.status == "out_of_domain",
            traces=_build_trace(
                request=request,
                module="extensions.hazard_failure.estimate_hazard_failure",
                manifest_version=self._manifest.version,
                extra={"uncertainty_reasons": decision.reasons},
            ),
            recommended_next_checks=["Re-estimate under alternative baseline hazard assumptions."],
        )

    def _call_scenario_tree_generator(self, request: WorldModelRequest) -> WorldModelResult:
        base_state = _coerce_float_mapping(request.payload["base_state"])
        uncertainty = _coerce_float_mapping(request.payload["uncertainty_drivers"])
        tree = generate_scenario_tree(
            base_state=base_state,
            uncertainty_drivers=uncertainty,
            branch_factor=float(request.payload.get("branch_factor", 0.2)),
        )
        policy = policy_from_dict(self._manifest.uncertainty_policies[request.tool_name])
        decision = route_uncertainty(
            UncertaintyRoutingInput(
                tool_name=request.tool_name,
                required_inputs=["base_state", "uncertainty_drivers"],
                provided_inputs=set(request.payload.keys()),
                confidence=0.64,
                variable_names=set(base_state),
            ),
            policy=policy,
        )
        branches = [
            {
                "name": branch.name,
                "probability": branch.probability,
                "assumptions": branch.assumptions,
            }
            for branch in tree.branches
        ]
        return WorldModelResult(
            tool_name=request.tool_name,
            summary="Scenario tree generated from current state and uncertainty drivers.",
            assumptions=["Branch probabilities are heuristic priors, not calibrated market odds."],
            modeled_variables=list(base_state.keys()),
            output={"branches": branches},
            uncertainty_status=decision.status,
            out_of_domain=decision.status == "out_of_domain",
            traces=_build_trace(
                request=request,
                module="extensions.scenario_tree_generator.generate_scenario_tree",
                manifest_version=self._manifest.version,
                extra={"uncertainty_reasons": decision.reasons},
            ),
            recommended_next_checks=[
                "Refine branch probabilities with updated uncertainty decomposition."
            ],
        )

    def _call_hidden_state_estimator(self, request: WorldModelRequest) -> WorldModelResult:
        indicators = _coerce_float_mapping(request.payload["indicators"])
        prior = (
            _coerce_float_mapping(request.payload["prior"]) if "prior" in request.payload else None
        )
        transition_bias = (
            _coerce_float_mapping(request.payload["transition_bias"])
            if "transition_bias" in request.payload
            else None
        )
        result = estimate_hidden_state(indicators, prior=prior, transition_bias=transition_bias)
        policy = policy_from_dict(self._manifest.uncertainty_policies[request.tool_name])
        confidence = result.confidence_band[1] - result.confidence_band[0]
        decision = route_uncertainty(
            UncertaintyRoutingInput(
                tool_name=request.tool_name,
                required_inputs=["indicators"],
                provided_inputs=set(request.payload.keys()),
                confidence=max(0.0, min(1.0, 1.0 - confidence)),
                variable_names=set(indicators),
            ),
            policy=policy,
        )
        return WorldModelResult(
            tool_name=request.tool_name,
            summary="Hidden state posterior estimated from indicator evidence.",
            assumptions=["Indicator-to-state mapping is heuristic and prior-sensitive."],
            modeled_variables=list(result.state_probabilities.keys()),
            output={
                "state_probabilities": result.state_probabilities,
                "most_likely_state": result.most_likely_state,
                "confidence_band": list(result.confidence_band),
            },
            uncertainty_status=decision.status,
            out_of_domain=decision.status == "out_of_domain",
            traces=_build_trace(
                request=request,
                module="extensions.hidden_state_estimator.estimate_hidden_state",
                manifest_version=self._manifest.version,
                extra={"uncertainty_reasons": decision.reasons},
            ),
            recommended_next_checks=["Compare hidden-state estimate under alternate priors."],
        )

    def _call_uncertainty_decomposition(self, request: WorldModelRequest) -> WorldModelResult:
        sensitivities = _coerce_float_mapping(request.payload["sensitivities"])
        parameter_uncertainty = _coerce_float_mapping(request.payload["parameter_uncertainty"])
        structural_uncertainty = (
            _coerce_float_mapping(request.payload["structural_uncertainty"])
            if "structural_uncertainty" in request.payload
            else None
        )
        result = decompose_uncertainty(
            sensitivities=sensitivities,
            parameter_uncertainty=parameter_uncertainty,
            structural_uncertainty=structural_uncertainty,
        )
        policy = policy_from_dict(self._manifest.uncertainty_policies[request.tool_name])
        decision = route_uncertainty(
            UncertaintyRoutingInput(
                tool_name=request.tool_name,
                required_inputs=["sensitivities", "parameter_uncertainty"],
                provided_inputs=set(request.payload.keys()),
                confidence=0.72,
                variable_names=set(sensitivities),
            ),
            policy=policy,
        )
        drivers = [
            {
                "name": driver.name,
                "contribution": driver.contribution,
                "normalized_weight": driver.normalized_weight,
            }
            for driver in result.drivers
        ]
        return WorldModelResult(
            tool_name=request.tool_name,
            summary="Uncertainty decomposition ranked dominant decision drivers.",
            assumptions=["Sensitivity and uncertainty inputs are directionally valid."],
            modeled_variables=[str(driver["name"]) for driver in drivers],
            output={
                "drivers": drivers,
                "dominant_driver": result.dominant_driver,
                "concentration_index": result.concentration_index,
            },
            uncertainty_status=decision.status,
            out_of_domain=decision.status == "out_of_domain",
            traces=_build_trace(
                request=request,
                module="extensions.uncertainty_decomposition.decompose_uncertainty",
                manifest_version=self._manifest.version,
                extra={"uncertainty_reasons": decision.reasons},
            ),
            recommended_next_checks=["Validate top-ranked driver against scenario ablations."],
        )

    def _call_value_of_information(self, request: WorldModelRequest) -> WorldModelResult:
        uncertainty_weights = _coerce_float_mapping(request.payload["uncertainty_weights"])
        information_gain = _coerce_float_mapping(request.payload["information_gain"])
        result = value_of_information(
            action_gap=float(request.payload["action_gap"]),
            uncertainty_weights=uncertainty_weights,
            information_gain=information_gain,
        )
        policy = policy_from_dict(self._manifest.uncertainty_policies[request.tool_name])
        decision = route_uncertainty(
            UncertaintyRoutingInput(
                tool_name=request.tool_name,
                required_inputs=["action_gap", "uncertainty_weights", "information_gain"],
                provided_inputs=set(request.payload.keys()),
                confidence=0.74,
                variable_names=set(uncertainty_weights) | set(information_gain),
            ),
            policy=policy,
        )
        candidates = [
            {
                "signal_name": candidate.signal_name,
                "voi_score": candidate.voi_score,
                "decision_flip_probability": candidate.decision_flip_probability,
            }
            for candidate in result.ranked_candidates
        ]
        return WorldModelResult(
            tool_name=request.tool_name,
            summary="Value-of-information ranking computed for candidate signals.",
            assumptions=["Action gap and information gain estimates are approximately calibrated."],
            modeled_variables=[str(item["signal_name"]) for item in candidates],
            output={
                "ranked_candidates": candidates,
                "best_next_signal": result.best_next_signal,
            },
            uncertainty_status=decision.status,
            out_of_domain=decision.status == "out_of_domain",
            traces=_build_trace(
                request=request,
                module="extensions.value_of_information.value_of_information",
                manifest_version=self._manifest.version,
                extra={"uncertainty_reasons": decision.reasons},
            ),
            recommended_next_checks=[
                "Cross-check VOI ranking under alternate action-gap assumptions."
            ],
        )

    def _call_model_arbitration(self, request: WorldModelRequest) -> WorldModelResult:
        model_outputs = _coerce_float_mapping(request.payload["model_outputs"])
        calibration_scores = (
            _coerce_float_mapping(request.payload["calibration_scores"])
            if "calibration_scores" in request.payload
            else None
        )
        validity_signals = (
            _coerce_float_mapping(request.payload["validity_signals"])
            if "validity_signals" in request.payload
            else None
        )
        result = arbitrate_models(
            model_outputs=model_outputs,
            calibration_scores=calibration_scores,
            validity_signals=validity_signals,
        )
        policy = policy_from_dict(self._manifest.uncertainty_policies[request.tool_name])
        confidence = max(0.0, min(1.0, 1.0 - result.disagreement_score))
        decision = route_uncertainty(
            UncertaintyRoutingInput(
                tool_name=request.tool_name,
                required_inputs=["model_outputs"],
                provided_inputs=set(request.payload.keys()),
                confidence=confidence,
                variable_names=set(model_outputs),
            ),
            policy=policy,
        )
        return WorldModelResult(
            tool_name=request.tool_name,
            summary="Model arbitration completed with disagreement diagnostics.",
            assumptions=["Calibration/validity metadata are representative of model reliability."],
            modeled_variables=list(model_outputs.keys()),
            output={
                "combined_estimate": result.combined_estimate,
                "disagreement_score": result.disagreement_score,
                "model_weights": result.model_weights,
                "mismatch_warning": result.mismatch_warning,
            },
            uncertainty_status=decision.status,
            out_of_domain=decision.status == "out_of_domain",
            traces=_build_trace(
                request=request,
                module="extensions.model_arbitration.arbitrate_models",
                manifest_version=self._manifest.version,
                extra={"uncertainty_reasons": decision.reasons},
            ),
            recommended_next_checks=[
                "Inspect disagreement score before acting on blended estimate."
            ],
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
