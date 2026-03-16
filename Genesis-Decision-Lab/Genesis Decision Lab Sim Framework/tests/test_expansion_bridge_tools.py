from datetime import datetime

from forecasting_engine.orchestration.contracts import WorldModelRequest
from forecasting_engine.orchestration.world_model_bridge import WorldModelBridge


def test_world_model_bridge_calls_structural_causal_graph() -> None:
    bridge = WorldModelBridge()
    request = WorldModelRequest(
        tool_name="structural_causal_graph",
        task="estimate_intervention_effect",
        as_of=datetime(2026, 3, 15),
        payload={
            "baseline": {"sanctions": 0.4, "trade_flow": 0.6, "inflation": 0.3},
            "edges": [
                {"parent": "sanctions", "child": "trade_flow", "weight": -0.5},
                {"parent": "trade_flow", "child": "inflation", "weight": -0.3},
            ],
            "intervention_node": "sanctions",
            "intervention_delta": 0.2,
        },
    )

    result = bridge.call(request)

    assert result.tool_name == "structural_causal_graph"
    assert "downstream_effects" in result.output
    assert "causal_sensitivity" in result.output


def test_world_model_bridge_calls_actor_hazard_and_scenario_tools() -> None:
    bridge = WorldModelBridge()

    actor_result = bridge.call(
        WorldModelRequest(
            tool_name="actor_response",
            task="simulate_strategic_response",
            as_of=datetime(2026, 3, 15),
            payload={
                "actors": [
                    {"name": "state_a", "incentive": 0.8, "constraint": 0.3, "risk_tolerance": 0.7},
                    {"name": "state_b", "incentive": 0.5, "constraint": 0.4, "risk_tolerance": 0.4},
                ],
                "trigger_intensity": 0.6,
            },
        )
    )
    hazard_result = bridge.call(
        WorldModelRequest(
            tool_name="hazard_failure",
            task="estimate_failure_risk",
            as_of=datetime(2026, 3, 15),
            payload={"stress_level": 0.7, "vulnerability": 0.4, "horizon": 2.0},
        )
    )
    scenario_result = bridge.call(
        WorldModelRequest(
            tool_name="scenario_tree_generator",
            task="generate_scenarios",
            as_of=datetime(2026, 3, 15),
            payload={
                "base_state": {"growth": 0.2, "inflation": 0.3},
                "uncertainty_drivers": {"growth": 0.6, "inflation": 0.4},
                "branch_factor": 0.15,
            },
        )
    )

    assert "action_probabilities" in actor_result.output
    assert 0.0 <= float(hazard_result.output["event_probability"]) <= 1.0
    assert len(scenario_result.output["branches"]) == 3


def test_world_model_bridge_calls_network_contagion() -> None:
    bridge = WorldModelBridge()
    request = WorldModelRequest(
        tool_name="network_contagion",
        task="propagate_cascade",
        as_of=datetime(2026, 3, 15),
        payload={
            "node_states": {"bank_a": 0.7, "bank_b": 0.2, "bank_c": 0.1},
            "edges": [
                {"source": "bank_a", "target": "bank_b", "weight": 0.4},
                {"source": "bank_b", "target": "bank_c", "weight": 0.5},
            ],
            "trigger_node": "bank_a",
            "trigger_delta": 0.2,
            "threshold": 0.5,
        },
    )

    result = bridge.call(request)

    assert result.tool_name == "network_contagion"
    assert 0.0 <= float(result.output["cascade_likelihood"]) <= 1.0
    assert result.output["critical_nodes"]
