from __future__ import annotations

import math
from typing import Any

from forecasting_engine.policies.contracts import PolicyResult

version = "regime-v1.1"


def validate_cfg(cfg: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cap = float(cfg.get("regime_cap", -1.0))
    if cap < 0:
        errors.append("regime_cap must be >= 0")
    return errors


def apply(state: dict[str, Any], evidence: dict[str, Any], cfg: dict[str, Any]) -> PolicyResult:
    del state
    del evidence
    del cfg
    raise NotImplementedError("Use regime_posterior and apply_regime_offset")


def explain(artifacts: dict[str, Any]) -> dict[str, Any]:
    return {
        "regime_post": artifacts.get("regime_post", []),
        "regime_entropy": artifacts.get("regime_entropy", 0.0),
        "regime_adjustment": artifacts.get("regime_adjustment", 0.0),
        "regime_cap_hit": artifacts.get("regime_cap_hit", False),
    }


def regime_posterior(signals: dict[str, float]) -> list[float]:
    values = [abs(v) for v in signals.values()]
    total = sum(values)
    if total == 0:
        return [1.0]
    return [v / total for v in values]


def entropy(values: list[float]) -> float:
    e = 0.0
    for value in values:
        p = max(min(value, 1.0), 1e-12)
        e += -p * math.log(p)
    return e


def apply_regime_offset(
    current_logodds: float,
    question_id: str,
    signals: dict[str, float],
    cfg: dict[str, Any],
) -> PolicyResult:
    weighted_signal = 0.0
    for signal, weight in cfg["weekly_signal_weights"].items():
        weighted_signal += float(signals.get(signal, 0.0)) * float(weight)
    question_adj = float(cfg["question_adjustments"].get(question_id, 0.0))
    raw_adj = weighted_signal * question_adj
    cap = float(cfg["regime_cap"])
    adjustment = max(min(raw_adj, cap), -cap)
    post = current_logodds + adjustment
    posterior = regime_posterior(signals)
    artifacts = {
        "regime_post": posterior,
        "regime_entropy": entropy(posterior),
        "regime_adjustment": adjustment,
        "regime_cap_hit": abs(raw_adj) > cap,
    }
    return PolicyResult(post, artifacts)
