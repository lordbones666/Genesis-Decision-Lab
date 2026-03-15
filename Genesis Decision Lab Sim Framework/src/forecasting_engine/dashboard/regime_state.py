from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegimeStateSummary:
    as_of: str
    regime_probabilities: dict[str, float]
    top_drivers: tuple[str, ...]
    recent_changes: dict[str, float]


def build_regime_state_summary(
    *,
    as_of: str,
    regime_probabilities: dict[str, float],
    top_drivers: list[str],
    previous_regime_probabilities: dict[str, float] | None = None,
) -> RegimeStateSummary:
    previous = previous_regime_probabilities or {}
    deltas = {
        regime: round(prob - previous.get(regime, 0.0), 6)
        for regime, prob in sorted(regime_probabilities.items())
    }
    return RegimeStateSummary(
        as_of=as_of,
        regime_probabilities=dict(sorted(regime_probabilities.items())),
        top_drivers=tuple(top_drivers),
        recent_changes=deltas,
    )
