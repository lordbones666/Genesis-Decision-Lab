from datetime import UTC, datetime, timedelta

from forecasting_engine.extensions import (
    DependencyEdge,
    SourceMemoryStats,
    appraise,
    baseline_base_rate,
    baseline_indicator_logistic,
    baseline_last_value,
    decay_weight,
    detect_regime_vector,
    propagate_dependencies,
    quantiles,
    run_backtest,
    snapshot_to_evidence,
    source_reliability_modifier,
    threshold_ladder,
    trigger_delta,
)
from forecasting_engine.extensions.timeseries_to_evidence import TimeSeriesSnapshot
from forecasting_engine.extensions.valuation.appraiser import Comparable
from forecasting_engine.extensions.valuation.item_schema import ValuationItem


def test_numeric_thresholds_quantiles() -> None:
    samples = [1.0, 2.0, 3.0, 4.0, 5.0]
    ladder = threshold_ladder(samples, [2.0, 4.0])
    assert ladder[2.0] == 0.6
    q = quantiles(samples)
    assert q.p50 == 3.0


def test_timeseries_to_evidence() -> None:
    snap = TimeSeriesSnapshot("vix", datetime.now(UTC), 33.0, 20.0, "cboe", "")
    ev = snapshot_to_evidence(snap, medium_threshold=5.0)
    assert ev.direction == 1
    assert ev.magnitude in {"medium", "large"}


def test_regime_dependency_decay_memory() -> None:
    rv = detect_regime_vector(
        {"vix": 35.0, "inflation": 5.0, "pmi": 47.0, "conflict_intensity": 0.6}
    )
    assert rv.risk_off > 0.0
    base = {"a": 0.2, "b": 0.2}
    out = propagate_dependencies(base, [DependencyEdge("a", "b", 0.5)], "a", 0.2)
    assert out["b"] > base["b"]
    now = datetime.now(UTC)
    old = now - timedelta(days=2)
    assert decay_weight("combat_report", old, now) < 1.0
    modifier = source_reliability_modifier(SourceMemoryStats("s", 0.2, 0.3, 0.1))
    assert 0.2 <= modifier <= 1.1


def test_backtest_benchmarks_and_surprise() -> None:
    summary = run_backtest([0.2, 0.8], [0, 1])
    assert summary.mean_brier >= 0.0
    assert len(baseline_base_rate(0.5, 4)) == 4
    assert len(baseline_last_value(0.6, 3)) == 3
    assert len(baseline_indicator_logistic([0.0, 1.0], -0.1, 0.5)) == 2
    assert trigger_delta("embassy_evacuation") > 0


def test_valuation_appraiser() -> None:
    item = ValuationItem(
        "electronics", "XPhone", 2022, 0.8, "NYC", "private", datetime.now(UTC), True
    )
    comps = [
        Comparable(600.0, 0.7, 0.5, 1.0, 0.95),
        Comparable(650.0, 0.8, 0.2, 1.0, 1.0),
        Comparable(700.0, 0.9, 0.1, 1.05, 1.0),
    ]
    result = appraise(item, comps)
    assert result.p10 <= result.p50 <= result.p90
    assert 0.1 <= result.confidence <= 0.95
