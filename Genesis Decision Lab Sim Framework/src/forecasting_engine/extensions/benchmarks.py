from __future__ import annotations


def baseline_base_rate(prior: float, horizon_count: int) -> list[float]:
    return [prior for _ in range(horizon_count)]


def baseline_last_value(last_probability: float, horizon_count: int) -> list[float]:
    return [last_probability for _ in range(horizon_count)]


def baseline_indicator_logistic(indicators: list[float], bias: float, coef: float) -> list[float]:
    import math

    return [1 / (1 + math.exp(-(bias + coef * value))) for value in indicators]
