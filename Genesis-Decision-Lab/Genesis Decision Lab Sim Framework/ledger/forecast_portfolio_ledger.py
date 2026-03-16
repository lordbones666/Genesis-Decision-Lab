from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from forecasting_engine.ledger import JsonlLedger
from forecasting_engine.portfolio.contracts import ForecastPortfolio


class ForecastPortfolioLedger(JsonlLedger):
    def __init__(self, path: Path) -> None:
        super().__init__(path)

    def append_portfolio(self, portfolio: ForecastPortfolio) -> None:
        self.append(asdict(portfolio))
