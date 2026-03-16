from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationParams:
    calibration_version_id: str
    method: str
    alpha: float
    train_end_idx: int


def fit_temperature_policy(
    probabilities: list[float], outcomes: list[int], train_end_idx: int, calibration_version_id: str
) -> CalibrationParams:
    if train_end_idx <= 0 or train_end_idx >= len(probabilities):
        raise ValueError("train_end_idx must split past and future")
    train_probs = probabilities[:train_end_idx]
    train_outcomes = outcomes[:train_end_idx]
    best_alpha = 1.0
    best_loss = float("inf")
    for i in range(5, 31):
        alpha = i / 10.0
        loss = 0.0
        for prob, outcome in zip(train_probs, train_outcomes, strict=True):
            scaled = min(max(prob ** (1.0 / alpha), 1e-6), 1 - 1e-6)
            loss += (scaled - outcome) ** 2
        avg_loss = loss / len(train_probs)
        if avg_loss < best_loss:
            best_loss = avg_loss
            best_alpha = alpha
    return CalibrationParams(calibration_version_id, "temperature", best_alpha, train_end_idx)


def apply_temperature_policy(probability: float, params: CalibrationParams) -> float:
    scaled = min(max(probability ** (1.0 / params.alpha), 1e-6), 1 - 1e-6)
    return float(scaled)
