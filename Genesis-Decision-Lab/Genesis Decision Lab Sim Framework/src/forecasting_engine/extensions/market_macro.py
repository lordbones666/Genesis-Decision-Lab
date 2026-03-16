from __future__ import annotations


def detect_market_regime(indicators: dict[str, float]) -> str:
    inflation = indicators.get("inflation", 0.0)
    vix = indicators.get("vix", 0.0)
    credit_spread = indicators.get("credit_spread", 0.0)
    growth = indicators.get("pmi", 50.0)

    if vix > 30 or credit_spread > 2.5:
        return "liquidity_crisis"
    if inflation > 4.0 and growth < 50.0:
        return "inflation_shock"
    if growth < 48.0:
        return "recession"
    return "expansion"


def positioning_risk_score(signals: dict[str, float]) -> float:
    gamma = abs(signals.get("options_gamma", 0.0))
    futures = abs(signals.get("cftc_extreme", 0.0))
    etf_flow = abs(signals.get("etf_flow_z", 0.0))
    return min((gamma + futures + etf_flow) / 3.0, 1.0)
