from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExposureMetrics:
    concentration_score: float
    scenario_overlap_score: float
    correlated_risk_score: float


@dataclass(frozen=True)
class ForecastPortfolio:
    portfolio_id: str
    forecast_ids: tuple[str, ...]
    question_ids: tuple[str, ...]
    scenario_ids: tuple[str, ...]
    exposure_metrics: ExposureMetrics
    regime_sensitivity: dict[str, float]
    assumptions: tuple[str, ...]
    notes: str = ""
    metadata: dict[str, str] = field(default_factory=dict)


def validate_portfolio(portfolio: ForecastPortfolio) -> None:
    if not portfolio.portfolio_id:
        raise ValueError("portfolio_id is required")
    if not portfolio.forecast_ids:
        raise ValueError("forecast_ids must not be empty")
    if not portfolio.question_ids:
        raise ValueError("question_ids must not be empty")
