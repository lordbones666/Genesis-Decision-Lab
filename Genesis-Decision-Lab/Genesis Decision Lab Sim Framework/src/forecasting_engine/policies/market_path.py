from __future__ import annotations

import math
import random
from typing import Any

version = "market-path-v1.1"


def barrier_probability(
    initial_price: float,
    target_price: float,
    mu: float,
    sigma: float,
    days: int,
    runs: int,
    seed: int,
) -> tuple[float, dict[str, Any]]:
    rng = random.Random(seed)
    crossings = 0
    dt = 1.0 / 252.0
    for _ in range(runs):
        price = initial_price
        crossed = False
        for _ in range(days):
            shock = rng.gauss(0.0, 1.0)
            growth = (mu - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * shock
            price *= math.exp(growth)
            if price >= target_price:
                crossed = True
                break
        if crossed:
            crossings += 1
    probability = crossings / runs
    return probability, {
        "rng_seed": seed,
        "runs": runs,
        "model": "gbm_mc",
        "barrier_type": "up_crossing",
    }
