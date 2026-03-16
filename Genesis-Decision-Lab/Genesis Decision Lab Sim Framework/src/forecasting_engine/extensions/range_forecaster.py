from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RangeBin:
    label: str
    probability: float


def threshold_probabilities(samples: list[float], thresholds: list[float]) -> dict[float, float]:
    if not samples:
        raise ValueError("samples must be non-empty")
    total = len(samples)
    return {
        threshold: sum(1 for sample in samples if sample > threshold) / total
        for threshold in thresholds
    }


def histogram_distribution(samples: list[float], bin_edges: list[float]) -> list[RangeBin]:
    if len(bin_edges) < 2:
        raise ValueError("bin_edges must contain at least two edges")
    if not samples:
        raise ValueError("samples must be non-empty")

    total = len(samples)
    output: list[RangeBin] = []
    for idx in range(len(bin_edges) - 1):
        low = bin_edges[idx]
        high = bin_edges[idx + 1]
        count = sum(1 for sample in samples if low <= sample < high)
        output.append(RangeBin(label=f"{low}-{high}", probability=count / total))
    upper = bin_edges[-1]
    count_upper = sum(1 for sample in samples if sample >= upper)
    output.append(RangeBin(label=f"{upper}+", probability=count_upper / total))
    return output
