from __future__ import annotations

import math
from datetime import datetime

HALF_LIFE_BY_TYPE_HOURS = {
    "combat_report": 72.0,
    "economic_release": 24.0 * 21,
    "policy_change": 24.0 * 120,
}


def decay_weight(evidence_type: str, observed_at: datetime, as_of: datetime) -> float:
    half_life = HALF_LIFE_BY_TYPE_HOURS.get(evidence_type, 24.0 * 14)
    elapsed_hours = max((as_of - observed_at).total_seconds() / 3600.0, 0.0)
    if half_life <= 0:
        return 1.0
    return math.exp(-math.log(2) * elapsed_hours / half_life)
