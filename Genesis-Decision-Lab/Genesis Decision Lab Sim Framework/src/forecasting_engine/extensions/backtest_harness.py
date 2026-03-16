from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestSummary:
    mean_brier: float
    count: int


def run_backtest(probabilities: list[float], outcomes: list[int]) -> BacktestSummary:
    if len(probabilities) != len(outcomes):
        raise ValueError("probabilities and outcomes must have equal length")
    if not probabilities:
        raise ValueError("non-empty probabilities required")
    brier = [(p - y) ** 2 for p, y in zip(probabilities, outcomes, strict=True)]
    return BacktestSummary(mean_brier=sum(brier) / len(brier), count=len(brier))
