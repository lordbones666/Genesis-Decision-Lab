from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuantileSummary:
    p10: float
    p50: float
    p90: float


def threshold_ladder(samples: list[float], thresholds: list[float]) -> dict[float, float]:
    if not samples:
        raise ValueError("samples must be non-empty")
    n = len(samples)
    return {t: sum(1 for value in samples if value > t) / n for t in thresholds}


def quantiles(samples: list[float]) -> QuantileSummary:
    if not samples:
        raise ValueError("samples must be non-empty")
    ordered = sorted(samples)

    def pick(q: float) -> float:
        idx = int((len(ordered) - 1) * q)
        return ordered[idx]

    return QuantileSummary(p10=pick(0.10), p50=pick(0.50), p90=pick(0.90))
