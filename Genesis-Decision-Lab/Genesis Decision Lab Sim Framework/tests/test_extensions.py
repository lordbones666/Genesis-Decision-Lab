from datetime import datetime, timezone

from forecasting_engine.extensions import (
    TacticalSignal,
    blend_structural_with_event,
    compile_vague_question,
    detect_market_regime,
    histogram_distribution,
    is_surprise_signal,
    misinformation_score,
    positioning_risk_score,
    propagate_event_shock,
    signal_weight,
    structural_logodds_offset,
    threshold_probabilities,
)


def test_range_forecast_outputs() -> None:
    samples = [80.0, 90.0, 100.0, 110.0, 120.0]
    thresholds = threshold_probabilities(samples, [90.0, 100.0])
    assert thresholds[90.0] == 0.6
    dist = histogram_distribution(samples, [70.0, 90.0, 110.0])
    assert abs(sum(row.probability for row in dist) - 1.0) < 1e-9


def test_osint_signal_weight_and_note() -> None:
    signal = TacticalSignal("tanker_launch_wave", datetime.now(timezone.utc), "USAF", 1.0, "adsb")
    assert signal_weight(signal) > 0.05


def test_structural_blend() -> None:
    offset = structural_logodds_offset({"inflation": 1.0, "sanctions": 0.5}, {"inflation": 0.2})
    assert offset == 0.2
    blended = blend_structural_with_event(0.4, 0.6, 0.25)
    assert abs(blended - 0.45) < 1e-9


def test_question_compiler_for_vague_prompt() -> None:
    compiled = compile_vague_question("Will the conflict get worse?")
    assert len(compiled) >= 3


def test_event_network_propagation() -> None:
    base = {"us_strike": 0.2, "iran_retaliation": 0.2, "hezbollah_escalation": 0.2}
    edges = [
        ("us_strike", "iran_retaliation", 0.5),
        ("iran_retaliation", "hezbollah_escalation", 0.5),
    ]
    updated = propagate_event_shock(base, edges, "us_strike", 0.2)
    assert updated["iran_retaliation"] > base["iran_retaliation"]


def test_surprise_and_misinfo() -> None:
    assert is_surprise_signal("embassy_evacuation")
    assessment = misinformation_score("tier_3", True, True, False)
    assert assessment.is_likely_misinformation


def test_market_regime_and_positioning() -> None:
    regime = detect_market_regime(
        {"vix": 35.0, "credit_spread": 3.0, "inflation": 3.0, "pmi": 51.0}
    )
    assert regime == "liquidity_crisis"
    score = positioning_risk_score({"options_gamma": 0.7, "cftc_extreme": 0.9, "etf_flow_z": 0.8})
    assert 0.0 <= score <= 1.0
