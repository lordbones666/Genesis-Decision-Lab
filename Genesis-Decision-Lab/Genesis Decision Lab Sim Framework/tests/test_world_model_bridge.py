from datetime import datetime

from forecasting_engine.orchestration.contracts import WorldModelRequest
from forecasting_engine.orchestration.world_model_bridge import WorldModelBridge


def test_world_model_bridge_calls_bayesian_update() -> None:
    bridge = WorldModelBridge()
    request = WorldModelRequest(
        tool_name="bayesian_update",
        task="update_event_probability",
        as_of=datetime(2026, 3, 14),
        payload={
            "prior": 0.4,
            "evidence": [
                {"evidence_id": "ev-1", "likelihood_ratio": 1.5, "weight": 1.0},
                {"evidence_id": "ev-2", "likelihood_ratio": 0.9, "weight": 0.6},
            ],
        },
    )

    result = bridge.call(request)

    assert result.tool_name == "bayesian_update"
    assert 0.0 < float(result.output["posterior"]) < 1.0
    assert result.uncertainty_status in {"valid", "partial", "out_of_domain"}
    assert result.traces["trace_id"].startswith("wm-")


def test_world_model_bridge_calls_monte_carlo() -> None:
    bridge = WorldModelBridge()
    request = WorldModelRequest(
        tool_name="monte_carlo_paths",
        task="estimate_threshold_hit_probability",
        as_of=datetime(2026, 3, 14),
        payload={
            "initial_value": 100.0,
            "threshold_value": 105.0,
            "mu": 0.08,
            "sigma": 0.15,
            "steps": 16,
            "runs": 80,
            "seed": 11,
        },
    )

    result = bridge.call(request)

    assert result.tool_name == "monte_carlo_paths"
    assert 0.0 <= float(result.output["threshold_hit_probability"]) <= 1.0
    assert "quantiles" in result.output


def test_world_model_bridge_calls_existing_domain_simulator() -> None:
    bridge = WorldModelBridge()
    request = WorldModelRequest(
        tool_name="domain_simulation",
        task="simulate_macro_scenario",
        as_of=datetime(2026, 3, 14),
        payload={
            "simulator_name": "macro_system",
            "inputs": {
                "global_growth": -0.2,
                "inflation_shock": 0.3,
                "policy_rate": 0.12,
                "energy_disruption": 0.25,
            },
            "scenario_id": "seed-e2e",
            "horizon_steps": 6,
            "seed": 17,
        },
    )

    result = bridge.call(request)

    assert result.tool_name == "domain_simulation"
    assert result.output["simulator"] == "macro_system"
    assert "state" in result.output
    assert result.traces["module"].endswith("SimulationOrchestrator.run")
    assert result.traces["manifest_version"] == "decision-lab-seed.v1"


def test_world_model_bridge_rejects_unknown_tool() -> None:
    bridge = WorldModelBridge()
    request = WorldModelRequest(
        tool_name="nonexistent_tool",
        task="unknown",
        as_of=datetime(2026, 3, 14),
        payload={},
    )

    result = bridge.call(request)

    assert result.out_of_domain is True
    assert result.failure_reason == "tool_not_in_manifest:nonexistent_tool"


def test_world_model_bridge_rejects_missing_required_inputs() -> None:
    bridge = WorldModelBridge()
    request = WorldModelRequest(
        tool_name="monte_carlo_paths",
        task="estimate_threshold_hit_probability",
        as_of=datetime(2026, 3, 14),
        payload={"initial_value": 100.0, "sigma": 0.2},
    )

    result = bridge.call(request)

    assert result.out_of_domain is True
    assert result.failure_reason is not None
    assert result.failure_reason.startswith("missing_required_inputs")
