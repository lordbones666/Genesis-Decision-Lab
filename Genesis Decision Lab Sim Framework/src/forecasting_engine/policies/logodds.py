from __future__ import annotations

import math
from typing import Any

from forecasting_engine.policies.contracts import PolicyResult

version = "logodds-v1.2"


def validate_cfg(cfg: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    eta = float(cfg.get("eta", 1.0))
    cap = float(cfg.get("cap", 0.0))
    cooldown_hours = float(cfg.get("cooldown_hours", -1.0))
    if not 0 < eta <= 1:
        errors.append("eta must satisfy 0 < eta <= 1")
    if cap <= 0:
        errors.append("cap must be > 0")
    if cooldown_hours < 0:
        errors.append("cooldown_hours must be >= 0")
    return errors


def apply(state: dict[str, Any], evidence: dict[str, Any], cfg: dict[str, Any]) -> PolicyResult:
    del state
    del evidence
    del cfg
    raise NotImplementedError("Use update_logodds_policy for explicit typed flow")


def explain(artifacts: dict[str, Any]) -> dict[str, Any]:
    return {
        "raw_llr_sum": artifacts.get("raw_llr_sum", 0.0),
        "delta_after_saturation": artifacts.get("delta_after_saturation", 0.0),
        "delta_cap_hit": artifacts.get("delta_cap_hit", False),
        "cooldown_multiplier": artifacts.get("cooldown_multiplier", 1.0),
    }


def update_logodds_policy(
    prior_logodds: float,
    evidence_deltas: list[float],
    cfg: dict[str, Any],
    cooldown_active: bool,
) -> PolicyResult:
    eta = float(cfg.get("eta", 1.0))
    cap = float(cfg["cap"])
    saturation = float(cfg["saturation"])
    cooldown_multiplier = 0.0 if cooldown_active else 1.0

    raw_llr_sum = sum(evidence_deltas)
    tempered = eta * raw_llr_sum
    if cooldown_active:
        clipped = 0.0
        delta = 0.0
    else:
        clipped = max(min(tempered, cap), -cap)
        delta = saturation * math.tanh(clipped)
    post_logodds = prior_logodds + delta
    artifacts = {
        "raw_llr_sum": raw_llr_sum,
        "tempered_llr": tempered,
        "clipped_llr": clipped,
        "delta_after_saturation": delta,
        "delta_cap_hit": abs(tempered) > cap,
        "cooldown_multiplier": cooldown_multiplier,
    }
    return PolicyResult(post_logodds, artifacts)
