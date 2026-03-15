from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TimeSeriesSnapshot:
    metric: str
    as_of: datetime
    current_value: float
    previous_value: float
    source: str
    unit: str = ""


@dataclass(frozen=True)
class TimeSeriesEvidence:
    claim: str
    direction: int
    magnitude: str
    delta_abs: float
    provenance: str


def snapshot_to_evidence(
    snapshot: TimeSeriesSnapshot, medium_threshold: float
) -> TimeSeriesEvidence:
    change = snapshot.current_value - snapshot.previous_value
    direction = 1 if change > 0 else (-1 if change < 0 else 0)
    abs_change = abs(change)
    if abs_change == 0:
        magnitude = "small"
    elif abs_change < medium_threshold:
        magnitude = "small"
    elif abs_change < 2 * medium_threshold:
        magnitude = "medium"
    else:
        magnitude = "large"
    claim = (
        f"{snapshot.metric} moved from {snapshot.previous_value:.4f} to {snapshot.current_value:.4f}"
        f" ({change:+.4f}{snapshot.unit})"
    )
    return TimeSeriesEvidence(
        claim=claim,
        direction=direction,
        magnitude=magnitude,
        delta_abs=abs_change,
        provenance=snapshot.source,
    )
