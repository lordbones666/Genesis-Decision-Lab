from __future__ import annotations

from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class HazardResult:
    hazard_rate: float
    survival_probability: float
    event_probability: float


def estimate_hazard_failure(
    stress_level: float,
    vulnerability: float,
    horizon: float,
    baseline_hazard: float = 0.03,
) -> HazardResult:
    hazard_rate = max(
        0.0, baseline_hazard + 0.4 * max(stress_level, 0.0) + 0.3 * max(vulnerability, 0.0)
    )
    survival = exp(-hazard_rate * max(horizon, 0.0))
    event_probability = 1.0 - survival
    return HazardResult(
        hazard_rate=hazard_rate,
        survival_probability=survival,
        event_probability=event_probability,
    )
