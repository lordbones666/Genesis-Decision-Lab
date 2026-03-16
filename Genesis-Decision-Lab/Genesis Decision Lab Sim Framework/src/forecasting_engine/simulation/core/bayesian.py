from __future__ import annotations

import math
from datetime import datetime

from forecasting_engine.simulation.contracts import BayesianEvidence, BayesianUpdateResult


def _clip_probability(value: float, epsilon: float = 1e-6) -> float:
    return min(max(value, epsilon), 1.0 - epsilon)


def _source_tier_multiplier(source_tier: str, tier_weights: dict[str, float]) -> float:
    return float(tier_weights.get(source_tier, tier_weights.get("default", 1.0)))


def _recency_decay(observed_at: datetime | None, as_of: datetime, half_life_days: float) -> float:
    if observed_at is None:
        return 1.0
    age_days = max((as_of - observed_at).total_seconds() / 86400.0, 0.0)
    if half_life_days <= 0:
        return 1.0
    return 2 ** (-age_days / half_life_days)


def bayesian_update(
    prior: float,
    evidence: list[BayesianEvidence],
    as_of: datetime,
    tier_weights: dict[str, float] | None = None,
    half_life_days: float = 90.0,
) -> BayesianUpdateResult:
    weights = tier_weights or {"default": 1.0}
    clipped_prior = _clip_probability(prior)
    prior_odds = clipped_prior / (1.0 - clipped_prior)

    effective_lr = 1.0
    for item in evidence:
        tier_mult = _source_tier_multiplier(item.source_tier, weights)
        decay_mult = _recency_decay(item.observed_at, as_of, half_life_days)
        weighted_lr = max(item.likelihood_ratio, 1e-6) ** (item.weight * tier_mult * decay_mult)
        effective_lr *= weighted_lr

    posterior_odds = prior_odds * effective_lr
    posterior = posterior_odds / (1.0 + posterior_odds)
    clipped_posterior = _clip_probability(posterior)

    # Approximate credible interval width from information strength.
    strength = max(abs(math.log(max(effective_lr, 1e-9))), 1e-6)
    half_width = min(0.45, 0.5 / math.sqrt(1.0 + 8.0 * strength))
    ci = (
        _clip_probability(clipped_posterior - half_width),
        _clip_probability(clipped_posterior + half_width),
    )

    return BayesianUpdateResult(
        prior=clipped_prior,
        posterior=clipped_posterior,
        effective_likelihood_ratio=effective_lr,
        confidence_interval=ci,
        explanation={
            "evidence_count": float(len(evidence)),
            "half_life_days": half_life_days,
            "update_mode": "likelihood_ratio",
        },
    )
