from datetime import datetime, timezone

from forecasting_engine.pipeline import monte_carlo, sr_to_seo, update_logodds, web_search_fetch

WEIGHTS = {
    "version": "weights-v1",
    "base_by_category": {"security": 0.35},
    "source_tier_multiplier": {"tier_1": 1.0},
    "delta_cap": 0.8,
    "cooldown_hours": 6,
    "saturation": 0.85,
}


def test_bitwise_determinism_for_same_inputs() -> None:
    as_of = datetime(2026, 1, 1, tzinfo=timezone.utc)
    srs = web_search_fetch("attack", [{"url": "https://example.com/a", "snippet": "attack"}])
    evidence = sr_to_seo("C1", srs, "security", "tier_1", 1, "small", "event")
    snap1 = update_logodds("C1", 0.5, evidence, WEIGHTS, None, as_of)
    snap2 = update_logodds("C1", 0.5, evidence, WEIGHTS, None, as_of)
    assert snap1.logodds == snap2.logodds
    assert snap1.delta_logodds == snap2.delta_logodds


def test_mc_determinism_same_seed() -> None:
    p1 = monte_carlo(70.0, 75.0, 0.0, 0.4, 30, 2000, seed=777)
    p2 = monte_carlo(70.0, 75.0, 0.0, 0.4, 30, 2000, seed=777)
    assert p1 == p2
