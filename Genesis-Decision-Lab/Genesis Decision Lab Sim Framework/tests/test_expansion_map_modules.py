from forecasting_engine.extensions import (
    arbitrate_models,
    decompose_uncertainty,
    estimate_hidden_state,
    value_of_information,
)


def test_hidden_state_estimator_returns_probabilities() -> None:
    estimate = estimate_hidden_state(
        indicators={"vix": 38.0, "pmi": 46.0, "inflation": 4.8, "conflict_intensity": 0.7}
    )
    assert estimate.most_likely_state in {"stable", "stressed", "crisis"}
    assert abs(sum(estimate.state_probabilities.values()) - 1.0) < 1e-9
    assert 0.0 <= estimate.confidence_band[0] <= estimate.confidence_band[1] <= 1.0


def test_uncertainty_decomposition_ranks_drivers() -> None:
    result = decompose_uncertainty(
        sensitivities={"policy": 0.8, "energy": 0.5, "supply": 0.3},
        parameter_uncertainty={"policy": 0.2, "energy": 0.4, "supply": 0.1},
        structural_uncertainty={"policy": 0.3, "energy": 0.1},
    )
    assert result.dominant_driver == "policy"
    assert result.drivers[0].normalized_weight >= result.drivers[-1].normalized_weight
    assert 0.0 < result.concentration_index <= 1.0


def test_value_of_information_selects_highest_signal() -> None:
    result = value_of_information(
        action_gap=0.08,
        uncertainty_weights={"satellite": 0.7, "shipping": 0.2, "sentiment": 0.3},
        information_gain={"satellite": 0.8, "shipping": 0.6, "sentiment": 0.1},
    )
    assert result.best_next_signal == "satellite"
    assert result.ranked_candidates[0].voi_score >= result.ranked_candidates[-1].voi_score


def test_model_arbitration_combines_and_flags_disagreement() -> None:
    result = arbitrate_models(
        model_outputs={"hmm": 0.25, "mc": 0.9, "causal": 0.2},
        calibration_scores={"hmm": 0.8, "mc": 0.6, "causal": 0.85},
        validity_signals={"hmm": 0.9, "mc": 0.5, "causal": 0.9},
    )
    assert 0.0 <= result.combined_estimate <= 1.0
    assert abs(sum(result.model_weights.values()) - 1.0) < 1e-9
    assert result.disagreement_score > 0.0
    assert result.mismatch_warning is True
