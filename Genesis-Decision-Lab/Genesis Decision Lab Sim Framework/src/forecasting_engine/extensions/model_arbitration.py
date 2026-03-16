from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArbitrationResult:
    combined_estimate: float
    disagreement_score: float
    model_weights: dict[str, float]
    mismatch_warning: bool


def arbitrate_models(
    model_outputs: dict[str, float],
    calibration_scores: dict[str, float] | None = None,
    validity_signals: dict[str, float] | None = None,
) -> ArbitrationResult:
    if not model_outputs:
        raise ValueError("model_outputs must not be empty")

    calibration_scores = calibration_scores or {}
    validity_signals = validity_signals or {}

    raw_weights: dict[str, float] = {}
    for model_name in model_outputs:
        calibration = max(0.0, min(1.0, float(calibration_scores.get(model_name, 0.5))))
        validity = max(0.0, min(1.0, float(validity_signals.get(model_name, 0.5))))
        raw_weights[model_name] = max(0.01, 0.2 + 0.8 * calibration * validity)

    weight_total = sum(raw_weights.values())
    weights = {name: value / weight_total for name, value in raw_weights.items()}
    combined = sum(float(model_outputs[name]) * weights[name] for name in model_outputs)
    disagreement = sum(
        weights[name] * abs(float(model_outputs[name]) - combined) for name in model_outputs
    )

    return ArbitrationResult(
        combined_estimate=combined,
        disagreement_score=disagreement,
        model_weights=weights,
        mismatch_warning=disagreement > 0.15,
    )
