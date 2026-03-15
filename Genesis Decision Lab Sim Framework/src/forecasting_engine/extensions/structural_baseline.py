from __future__ import annotations


def structural_logodds_offset(indicators: dict[str, float], weights: dict[str, float]) -> float:
    return sum(indicators.get(key, 0.0) * value for key, value in weights.items())


def blend_structural_with_event(
    event_probability: float, structural_probability: float, alpha: float
) -> float:
    bounded_alpha = min(max(alpha, 0.0), 1.0)
    return (1.0 - bounded_alpha) * event_probability + bounded_alpha * structural_probability
