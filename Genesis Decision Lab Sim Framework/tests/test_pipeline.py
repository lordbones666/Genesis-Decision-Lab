from datetime import datetime, timezone
from typing import Any, cast

from forecasting_engine.pipeline import (
    apply_reference_prior,
    dedupe_cluster,
    run_ablation_forecasts,
    sr_to_seo,
    update_logodds,
    web_search_fetch,
)

WEIGHTS: dict[str, Any] = {
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


def test_dedupe_prevents_double_counting() -> None:
    srs = web_search_fetch(
        "attack",
        [
            {
                "url": "https://example.com/a",
                "publisher": "example",
                "title": "A",
                "snippet": "attack",
            },
            {
                "url": "https://example.com/b",
                "publisher": "example",
                "title": "B",
                "snippet": "attack",
            },
        ],
    )
    seos = sr_to_seo("C1", srs, "security", "tier_1", 1, "small", "event")
    assert seos[0].cluster_id
    clustered, provenance = dedupe_cluster(seos)
    assert len(clustered) == 1
    assert len(provenance) == 2


def test_update_logodds_bounds_and_caps() -> None:
    srs = web_search_fetch(
        "attack",
        [
            {
                "url": "https://example.com/a",
                "publisher": "example",
                "title": "A",
                "snippet": "attack",
            }
        ],
    )
    evidence = sr_to_seo("C1", srs, "security", "tier_1", 1, "large", "event")
    snapshot = update_logodds(
        "C1",
        current_probability=0.5,
        evidence=evidence,
        weights=WEIGHTS,
        last_update_at=None,
        as_of=datetime.now(timezone.utc),
    )
    assert 0.0 < snapshot.probability < 1.0
    assert abs(snapshot.delta_logodds) <= cast(float, WEIGHTS["saturation"])
    assert abs(snapshot.delta_logodds) <= abs(snapshot.raw_delta_logodds)


def test_correction_reversal_uses_prior_delta() -> None:
    srs = web_search_fetch("corr", [{"url": "https://example.com/c", "snippet": "correction"}])
    correction = sr_to_seo(
        "C1",
        srs,
        "security",
        "tier_1",
        0,
        "small",
        "correction",
        correction_of_event_id="evt-prior",
    )
    snapshot = update_logodds(
        "C1",
        0.6,
        correction,
        WEIGHTS,
        None,
        datetime.now(timezone.utc),
        historical_event_deltas={"evt-prior": 0.2},
    )
    assert "evt-prior" in snapshot.reversal_of_event_ids


def test_ablation_outputs_default_set() -> None:
    srs = web_search_fetch("attack", [{"url": "https://example.com/a", "snippet": "attack"}])
    evidence = sr_to_seo("C1", srs, "security", "tier_1", 1, "small", "event")
    baseline = update_logodds("C1", 0.5, evidence, WEIGHTS, None, datetime.now(timezone.utc))
    outputs = run_ablation_forecasts(
        baseline,
        "C1",
        {"volatility": 0.5},
        REGIME,
        mc_probability=0.55,
    )
    assert set(outputs.keys()) == {"baseline", "with_regime", "with_regime_mc"}
    assert outputs["with_regime"].regime_entropy >= 0.0


def test_apply_reference_prior_clips_bounds() -> None:
    priors = {"key": 1.2}
    value = apply_reference_prior("key", priors)
    assert value < 1.0
    assert apply_reference_prior("unknown", priors) == 0.5
