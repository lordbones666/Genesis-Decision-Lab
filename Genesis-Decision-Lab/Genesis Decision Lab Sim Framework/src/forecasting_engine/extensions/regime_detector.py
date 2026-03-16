from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegimeVector:
    risk_on: float
    risk_off: float
    inflation_shock: float
    recession_risk: float
    war_escalation: float


def detect_regime_vector(features: dict[str, float]) -> RegimeVector:
    vix = features.get("vix", 20.0)
    inflation = features.get("inflation", 2.0)
    pmi = features.get("pmi", 52.0)
    conflict_intensity = features.get("conflict_intensity", 0.2)

    risk_off = min(max((vix - 20.0) / 20.0, 0.0), 1.0)
    risk_on = 1.0 - risk_off
    inflation_shock = min(max((inflation - 3.0) / 4.0, 0.0), 1.0)
    recession_risk = min(max((50.0 - pmi) / 10.0, 0.0), 1.0)
    war_escalation = min(max(conflict_intensity, 0.0), 1.0)
    return RegimeVector(risk_on, risk_off, inflation_shock, recession_risk, war_escalation)
