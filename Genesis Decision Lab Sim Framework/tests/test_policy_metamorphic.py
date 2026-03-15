from datetime import datetime, timezone

from forecasting_engine.pipeline import (
    run_ablation_forecasts,
    sr_to_seo,
    update_logodds,
    web_search_fetch,
)

WEIGHTS = {
    "version": "weights-v1",
    "base_by_category": {"security": 0.35},
    "source_tier_multiplier": {"tier_1": 1.0},
    "delta_cap": 0.8,
    "cooldown_hours": 6,
    "saturation": 0.85,
}

REGIME = {
    "weekly_signal_weights": {"volatility": 1.0},
    "question_adjustments": {"C1": 0.1},
    "regime_cap": 0.2,
}


def test_duplicate_evidence_has_bounded_effect() -> None:
    srs = web_search_fetch("attack", [{"url": "https://example.com/a", "snippet": "attack"}])
    one = sr_to_seo("C1", srs, "security", "tier_1", 1, "small", "event")
    ten = one * 10
    snap_one = update_logodds("C1", 0.5, one, WEIGHTS, None, datetime.now(timezone.utc))
    snap_ten = update_logodds("C1", 0.5, ten, WEIGHTS, None, datetime.now(timezone.utc))
    assert abs(snap_ten.delta_logodds - snap_one.delta_logodds) < 0.6


def test_order_invariance_same_timestamp_bucket() -> None:
    srs = web_search_fetch(
        "attack",
        [
            {"url": "https://example.com/a", "title": "A", "snippet": "attack"},
            {"url": "https://example.com/b", "title": "B", "snippet": "attack"},
        ],
    )
    first = sr_to_seo("C1", srs, "security", "tier_1", 1, "small", "event")
    second = list(reversed(first))
    snap_a = update_logodds("C1", 0.5, first, WEIGHTS, None, datetime.now(timezone.utc))
    snap_b = update_logodds("C1", 0.5, second, WEIGHTS, None, datetime.now(timezone.utc))
    assert round(snap_a.probability, 8) == round(snap_b.probability, 8)


def test_dependency_accounting_blocks_overlap_blend() -> None:
    srs = web_search_fetch("attack", [{"url": "https://example.com/a", "snippet": "attack"}])
    evidence = sr_to_seo("C1", srs, "security", "tier_1", 1, "small", "event")
    baseline = update_logodds("C1", 0.5, evidence, WEIGHTS, None, datetime.now(timezone.utc))
    out = run_ablation_forecasts(
        baseline,
        "C1",
        {"volatility": 0.3},
        REGIME,
        mc_probability=0.9,
        baseline_features={"wti_spot", "ovx"},
        mc_features={"ovx"},
        allow_feature_overlap=False,
    )
    dep = out["with_regime_mc"].artifacts.get("dependency", {})
    assert dep.get("dependency_blocked") is True
