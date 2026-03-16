from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UncertaintyDriver:
    name: str
    contribution: float
    normalized_weight: float


@dataclass(frozen=True)
class UncertaintyDecomposition:
    drivers: list[UncertaintyDriver]
    dominant_driver: str
    concentration_index: float


def decompose_uncertainty(
    sensitivities: dict[str, float],
    parameter_uncertainty: dict[str, float],
    structural_uncertainty: dict[str, float] | None = None,
) -> UncertaintyDecomposition:
    structural_uncertainty = structural_uncertainty or {}
    contributions: dict[str, float] = {}
    all_keys = set(sensitivities) | set(parameter_uncertainty) | set(structural_uncertainty)

    for key in all_keys:
        sensitivity = abs(float(sensitivities.get(key, 0.0)))
        param_sigma = max(float(parameter_uncertainty.get(key, 0.0)), 0.0)
        structure_sigma = max(float(structural_uncertainty.get(key, 0.0)), 0.0)
        contributions[key] = sensitivity * (param_sigma + structure_sigma)

    total = sum(contributions.values())
    if total <= 0.0:
        return UncertaintyDecomposition(drivers=[], dominant_driver="none", concentration_index=0.0)

    ranked = sorted(contributions.items(), key=lambda item: item[1], reverse=True)
    drivers = [
        UncertaintyDriver(
            name=name,
            contribution=value,
            normalized_weight=value / total,
        )
        for name, value in ranked
    ]
    concentration = sum(driver.normalized_weight**2 for driver in drivers)
    return UncertaintyDecomposition(
        drivers=drivers,
        dominant_driver=drivers[0].name,
        concentration_index=concentration,
    )
