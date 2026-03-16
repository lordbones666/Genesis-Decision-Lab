from __future__ import annotations

from forecasting_engine.portfolio.contracts import ExposureMetrics


def summarize_exposure(
    forecast_weights: dict[str, float],
    scenario_overlap: dict[str, float],
    correlation_pairs: dict[str, float],
) -> ExposureMetrics:
    total = sum(max(weight, 0.0) for weight in forecast_weights.values()) or 1.0
    concentration = max(forecast_weights.values(), default=0.0) / total
    overlap = sum(abs(value) for value in scenario_overlap.values()) / (len(scenario_overlap) or 1)
    correlated = sum(abs(value) for value in correlation_pairs.values()) / (
        len(correlation_pairs) or 1
    )
    return ExposureMetrics(
        concentration_score=round(concentration, 6),
        scenario_overlap_score=round(overlap, 6),
        correlated_risk_score=round(correlated, 6),
    )
