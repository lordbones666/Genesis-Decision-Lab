from __future__ import annotations

import math
import random
from dataclasses import dataclass

from forecasting_engine.policies.market_path import barrier_probability
from forecasting_engine.simulation.contracts import MonteCarloPathResult, MonteCarloRunSummary


@dataclass(frozen=True)
class MonteCarloConfig:
    steps: int
    runs: int
    dt: float = 1.0 / 252.0
    jump_probability: float = 0.0
    jump_mean: float = 0.0
    jump_std: float = 0.0


def _path_step(
    value: float,
    mu: float,
    sigma: float,
    cfg: MonteCarloConfig,
    rng: random.Random,
) -> float:
    shock = rng.gauss(0.0, 1.0)
    jump = 0.0
    if cfg.jump_probability > 0.0 and rng.random() < cfg.jump_probability:
        jump = rng.gauss(cfg.jump_mean, cfg.jump_std)
    diffusion = (mu - 0.5 * sigma**2) * cfg.dt + sigma * math.sqrt(cfg.dt) * shock
    return value * math.exp(diffusion + jump)


def run_paths(
    initial_value: float,
    threshold_value: float,
    mu: float,
    sigma: float,
    seed: int,
    cfg: MonteCarloConfig,
) -> tuple[MonteCarloRunSummary, list[MonteCarloPathResult]]:
    rng = random.Random(seed)
    path_results: list[MonteCarloPathResult] = []
    finals: list[float] = []
    hit_count = 0

    for _ in range(cfg.runs):
        value = initial_value
        max_value = value
        min_value = value
        hit_threshold = False
        for _ in range(cfg.steps):
            value = _path_step(value, mu, sigma, cfg, rng)
            max_value = max(max_value, value)
            min_value = min(min_value, value)
            if value >= threshold_value:
                hit_threshold = True
        finals.append(value)
        hit_count += int(hit_threshold)
        path_results.append(
            MonteCarloPathResult(
                final_value=value,
                hit_threshold=hit_threshold,
                max_value=max_value,
                min_value=min_value,
            )
        )

    ordered = sorted(finals)

    def _q(p: float) -> float:
        idx = min(max(int(round((len(ordered) - 1) * p)), 0), len(ordered) - 1)
        return ordered[idx]

    summary = MonteCarloRunSummary(
        threshold_hit_probability=hit_count / cfg.runs,
        mean_final_value=sum(finals) / len(finals),
        quantiles={"p10": _q(0.1), "p50": _q(0.5), "p90": _q(0.9)},
        model="general_mc_jump_diffusion",
        seed=seed,
    )
    return summary, path_results


def legacy_market_barrier_bridge(
    initial_price: float,
    target_price: float,
    mu: float,
    sigma: float,
    days: int,
    runs: int,
    seed: int,
) -> MonteCarloRunSummary:
    probability, _ = barrier_probability(initial_price, target_price, mu, sigma, days, runs, seed)
    return MonteCarloRunSummary(
        threshold_hit_probability=probability,
        mean_final_value=initial_price,
        quantiles={},
        model="legacy_market_path_bridge",
        seed=seed,
    )
