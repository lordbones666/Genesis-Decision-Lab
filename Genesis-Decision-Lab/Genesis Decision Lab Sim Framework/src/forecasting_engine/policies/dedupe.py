from __future__ import annotations

import hashlib
import math
from datetime import datetime
from typing import Any

version = "dedupe-v1.1"


def deterministic_cluster_id(key_fields: list[str]) -> str:
    return hashlib.sha256("|".join(key_fields).encode()).hexdigest()[:16]


def similarity_fingerprint(text: str, fingerprint_version: str = "simhash-v1") -> dict[str, str]:
    digest = hashlib.sha256(text.lower().encode()).hexdigest()
    return {"fingerprint": digest[:16], "fingerprint_version": fingerprint_version}


def aggregate_cluster(
    weights: list[float],
    c_max: float,
    tau_hours: float,
    last_seen_at: datetime | None,
    now: datetime,
) -> dict[str, Any]:
    raw = sum(weights)
    effective = c_max * math.tanh(raw / c_max) if c_max > 0 else raw
    if last_seen_at is None or tau_hours <= 0:
        cooldown_multiplier = 1.0
    else:
        dt_hours = max((now - last_seen_at).total_seconds() / 3600.0, 0.0)
        cooldown_multiplier = 1.0 - math.exp(-dt_hours / tau_hours)
    adjusted = cooldown_multiplier * effective
    return {
        "raw_cluster_sum": raw,
        "effective_cluster_sum": effective,
        "cooldown_multiplier": cooldown_multiplier,
        "adjusted_cluster_sum": adjusted,
    }
