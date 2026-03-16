from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceMemoryStats:
    source_id: str
    retraction_rate: float
    brier_mean: float
    propaganda_risk: float


def source_reliability_modifier(stats: SourceMemoryStats) -> float:
    score = 1.0
    score -= min(max(stats.retraction_rate, 0.0), 1.0) * 0.35
    score -= min(max(stats.brier_mean, 0.0), 1.0) * 0.25
    score -= min(max(stats.propaganda_risk, 0.0), 1.0) * 0.40
    return min(max(score, 0.2), 1.1)
