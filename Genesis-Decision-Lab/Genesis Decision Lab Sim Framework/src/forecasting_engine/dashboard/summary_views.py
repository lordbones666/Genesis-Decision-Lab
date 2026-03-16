from __future__ import annotations

from dataclasses import dataclass

from forecasting_engine.dashboard.regime_state import RegimeStateSummary


@dataclass(frozen=True)
class DecisionLabSummaryView:
    regime: RegimeStateSummary
    impacted_scenarios: tuple[str, ...]
    impacted_portfolios: tuple[str, ...]
    impacted_forecasts: tuple[str, ...]


def assemble_summary_view(
    regime: RegimeStateSummary,
    impacted_scenarios: list[str],
    impacted_portfolios: list[str],
    impacted_forecasts: list[str],
) -> DecisionLabSummaryView:
    return DecisionLabSummaryView(
        regime=regime,
        impacted_scenarios=tuple(sorted(set(impacted_scenarios))),
        impacted_portfolios=tuple(sorted(set(impacted_portfolios))),
        impacted_forecasts=tuple(sorted(set(impacted_forecasts))),
    )
