from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiCandidate:
    signal_name: str
    voi_score: float
    decision_flip_probability: float


@dataclass(frozen=True)
class ValueOfInformationResult:
    ranked_candidates: list[VoiCandidate]
    best_next_signal: str


def value_of_information(
    action_gap: float,
    uncertainty_weights: dict[str, float],
    information_gain: dict[str, float],
) -> ValueOfInformationResult:
    effective_gap = max(abs(action_gap), 1e-6)
    candidates: list[VoiCandidate] = []
    for signal_name in set(uncertainty_weights) | set(information_gain):
        uncertainty = max(0.0, float(uncertainty_weights.get(signal_name, 0.0)))
        gain = max(0.0, float(information_gain.get(signal_name, 0.0)))
        flip_probability = min(1.0, (uncertainty * gain) / (effective_gap + uncertainty * gain))
        candidates.append(
            VoiCandidate(
                signal_name=signal_name,
                voi_score=uncertainty * gain,
                decision_flip_probability=flip_probability,
            )
        )

    ranked = sorted(
        candidates,
        key=lambda candidate: (candidate.voi_score, candidate.decision_flip_probability),
        reverse=True,
    )
    if not ranked:
        return ValueOfInformationResult(ranked_candidates=[], best_next_signal="none")
    return ValueOfInformationResult(
        ranked_candidates=ranked, best_next_signal=ranked[0].signal_name
    )
