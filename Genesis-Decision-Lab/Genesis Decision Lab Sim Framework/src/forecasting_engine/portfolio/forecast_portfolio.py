from __future__ import annotations

from forecasting_engine.portfolio.contracts import ForecastPortfolio, validate_portfolio
from forecasting_engine.portfolio.exposure import summarize_exposure


def build_forecast_portfolio(
    *,
    portfolio_id: str,
    forecast_ids: list[str],
    question_ids: list[str],
    scenario_ids: list[str],
    forecast_weights: dict[str, float],
    scenario_overlap: dict[str, float],
    correlation_pairs: dict[str, float],
    regime_sensitivity: dict[str, float],
    assumptions: list[str],
    notes: str = "",
) -> ForecastPortfolio:
    portfolio = ForecastPortfolio(
        portfolio_id=portfolio_id,
        forecast_ids=tuple(sorted(set(forecast_ids))),
        question_ids=tuple(sorted(set(question_ids))),
        scenario_ids=tuple(sorted(set(scenario_ids))),
        exposure_metrics=summarize_exposure(forecast_weights, scenario_overlap, correlation_pairs),
        regime_sensitivity=dict(sorted(regime_sensitivity.items())),
        assumptions=tuple(assumptions),
        notes=notes,
    )
    validate_portfolio(portfolio)
    return portfolio
