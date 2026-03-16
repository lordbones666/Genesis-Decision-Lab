from __future__ import annotations

from dataclasses import dataclass

from forecasting_engine.extensions.numeric_thresholds import QuantileSummary
from forecasting_engine.extensions.valuation.item_schema import ValuationItem


@dataclass(frozen=True)
class Comparable:
    price: float
    condition_grade: float
    age_years: float
    location_factor: float
    channel_factor: float


@dataclass(frozen=True)
class AppraisalResult:
    p10: float
    p50: float
    p90: float
    recommended_list_price: float
    recommended_quick_sale_price: float
    confidence: float


def _adjust_comp(comp: Comparable, target: ValuationItem) -> float:
    condition_adj = 1 + 0.12 * (target.condition_grade - comp.condition_grade)
    time_adj = 1 - 0.015 * comp.age_years
    location_adj = comp.location_factor
    channel_adj = comp.channel_factor
    raw = comp.price * condition_adj * time_adj * location_adj * channel_adj
    return max(raw, 0.0)


def _quantiles(values: list[float]) -> QuantileSummary:
    ordered = sorted(values)

    def pick(q: float) -> float:
        idx = int((len(ordered) - 1) * q)
        return ordered[idx]

    return QuantileSummary(p10=pick(0.10), p50=pick(0.50), p90=pick(0.90))


def appraise(target: ValuationItem, comps: list[Comparable]) -> AppraisalResult:
    if not comps:
        raise ValueError("At least one comparable required")
    adjusted = [_adjust_comp(comp, target) for comp in comps]
    q = _quantiles(adjusted)
    spread = max(q.p90 - q.p10, 1e-6)
    confidence = min(max(len(comps) / 20.0 * (1.0 / (1 + spread / max(q.p50, 1e-6))), 0.1), 0.95)
    return AppraisalResult(
        p10=q.p10,
        p50=q.p50,
        p90=q.p90,
        recommended_list_price=q.p50,
        recommended_quick_sale_price=q.p10,
        confidence=confidence,
    )
