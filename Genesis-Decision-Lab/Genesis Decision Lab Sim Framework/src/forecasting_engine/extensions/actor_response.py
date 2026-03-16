from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActorProfile:
    name: str
    incentive: float
    constraint: float
    risk_tolerance: float


@dataclass(frozen=True)
class ActorResponseResult:
    action_probabilities: dict[str, float]
    strategic_branches: list[str]
    adversarial_risk: float


def simulate_actor_response(
    actors: list[ActorProfile],
    trigger_intensity: float,
    policy_pressure: float = 0.0,
) -> ActorResponseResult:
    if not actors:
        return ActorResponseResult(
            action_probabilities={}, strategic_branches=[], adversarial_risk=0.0
        )

    weights: dict[str, float] = {}
    for actor in actors:
        intent = actor.incentive * (1.0 + trigger_intensity)
        friction = max(0.05, 1.0 + actor.constraint + policy_pressure)
        risk = max(0.05, actor.risk_tolerance)
        weights[actor.name] = max(0.01, intent * risk / friction)

    total = sum(weights.values())
    probabilities = {name: weight / total for name, weight in weights.items()}
    branches = [
        name for name, _ in sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
    ]
    adversarial_risk = sum(
        probabilities[actor.name] * max(0.0, actor.risk_tolerance - actor.constraint)
        for actor in actors
    )

    return ActorResponseResult(
        action_probabilities=probabilities,
        strategic_branches=branches,
        adversarial_risk=adversarial_risk,
    )
