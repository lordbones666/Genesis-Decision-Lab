from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HiddenStateEstimate:
    state_probabilities: dict[str, float]
    most_likely_state: str
    confidence_band: tuple[float, float]


def estimate_hidden_state(
    indicators: dict[str, float],
    prior: dict[str, float] | None = None,
    transition_bias: dict[str, float] | None = None,
) -> HiddenStateEstimate:
    states = ("stable", "stressed", "crisis")
    prior_probs = _normalize_probs(
        prior or {"stable": 0.5, "stressed": 0.35, "crisis": 0.15}, states
    )
    bias = transition_bias or {}

    stress_score = _bounded(
        0.35 * _bounded((indicators.get("vix", 20.0) - 20.0) / 25.0)
        + 0.25 * _bounded((3.5 - indicators.get("pmi", 50.0)) / 6.0)
        + 0.2 * _bounded((indicators.get("inflation", 2.5) - 2.5) / 3.5)
        + 0.2 * _bounded(indicators.get("conflict_intensity", 0.2))
    )

    likelihoods = {
        "stable": max(0.01, 1.0 - stress_score),
        "stressed": max(0.01, 0.2 + 1.2 * abs(stress_score - 0.5)),
        "crisis": max(0.01, 0.05 + 1.25 * stress_score),
    }

    weighted: dict[str, float] = {}
    for state in states:
        weighted[state] = prior_probs[state] * likelihoods[state] * float(bias.get(state, 1.0))

    posterior = _normalize_probs(weighted, states)
    ranked = sorted(posterior.items(), key=lambda item: item[1], reverse=True)
    top, second = ranked[0], ranked[1]
    margin = top[1] - second[1]
    half_width = max(0.02, (1.0 - margin) * 0.35)
    band = (_bounded(top[1] - half_width), _bounded(top[1] + half_width))

    return HiddenStateEstimate(
        state_probabilities=posterior,
        most_likely_state=top[0],
        confidence_band=band,
    )


def _normalize_probs(values: dict[str, float], states: tuple[str, ...]) -> dict[str, float]:
    total = sum(max(0.0, float(values.get(state, 0.0))) for state in states)
    if total <= 0.0:
        even = 1.0 / float(len(states))
        return {state: even for state in states}
    return {state: max(0.0, float(values.get(state, 0.0))) / total for state in states}


def _bounded(value: float) -> float:
    return min(max(value, 0.0), 1.0)
