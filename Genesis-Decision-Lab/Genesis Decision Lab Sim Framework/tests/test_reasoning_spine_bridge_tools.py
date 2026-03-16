from datetime import datetime

from forecasting_engine.orchestration.contracts import WorldModelRequest
from forecasting_engine.orchestration.world_model_bridge import WorldModelBridge


def test_bridge_calls_hidden_state_estimator() -> None:
    bridge = WorldModelBridge()
    result = bridge.call(
        WorldModelRequest(
            tool_name="hidden_state_estimator",
            task="estimate latent state",
            as_of=datetime(2026, 3, 16),
            payload={"indicators": {"vix": 34.0, "pmi": 47.0, "inflation": 4.1}},
        )
    )
    assert result.tool_name == "hidden_state_estimator"
    assert "state_probabilities" in result.output


def test_bridge_calls_uncertainty_decomposition_voi_and_arbitration() -> None:
    bridge = WorldModelBridge()
    decomposition = bridge.call(
        WorldModelRequest(
            tool_name="uncertainty_decomposition",
            task="decompose uncertainty",
            as_of=datetime(2026, 3, 16),
            payload={
                "sensitivities": {"energy": 0.8, "policy": 0.4},
                "parameter_uncertainty": {"energy": 0.3, "policy": 0.2},
            },
        )
    )
    voi = bridge.call(
        WorldModelRequest(
            tool_name="value_of_information",
            task="value of information ranking",
            as_of=datetime(2026, 3, 16),
            payload={
                "action_gap": 0.08,
                "uncertainty_weights": {"satellite": 0.7, "shipping": 0.3},
                "information_gain": {"satellite": 0.8, "shipping": 0.4},
            },
        )
    )
    arbitration = bridge.call(
        WorldModelRequest(
            tool_name="model_arbitration",
            task="arbitrate model disagreement",
            as_of=datetime(2026, 3, 16),
            payload={
                "model_outputs": {"hmm": 0.3, "mc": 0.7, "causal": 0.5},
                "calibration_scores": {"hmm": 0.8, "mc": 0.6, "causal": 0.9},
                "validity_signals": {"hmm": 0.9, "mc": 0.7, "causal": 0.8},
            },
        )
    )

    assert decomposition.output["dominant_driver"] in {"energy", "policy"}
    assert voi.output["best_next_signal"] in {"satellite", "shipping"}
    assert 0.0 <= float(arbitration.output["combined_estimate"]) <= 1.0
