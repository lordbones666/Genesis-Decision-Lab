from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from forecasting_engine.models import ForecastSnapshot, ScoreRecord


@dataclass(frozen=True)
class CalibrationBin:
    lower: float
    upper: float
    count: int
    avg_pred: float
    avg_outcome: float


@dataclass(frozen=True)
class MonitoringAlert:
    should_freeze: bool
    reason: str
    suggested_alpha_shrink: float


def brier_score(probability: float, outcome: int) -> float:
    return (probability - outcome) ** 2


def score_forecasts(resolved: list[tuple[ForecastSnapshot, int, str, str]]) -> list[ScoreRecord]:
    rows: list[ScoreRecord] = []
    for snapshot, outcome, domain, horizon in resolved:
        rows.append(
            ScoreRecord(
                question_id=snapshot.question_id,
                resolved_at=snapshot.as_of,
                outcome=outcome,
                probability=snapshot.probability,
                brier=brier_score(snapshot.probability, outcome),
                domain=domain,
                horizon=horizon,
            )
        )
    return rows


def calibration_bins(scores: list[ScoreRecord], bins: int = 10) -> list[CalibrationBin]:
    width = 1.0 / bins
    grouped: dict[int, list[ScoreRecord]] = defaultdict(list)
    for score in scores:
        idx = min(int(score.probability / width), bins - 1)
        grouped[idx].append(score)
    output: list[CalibrationBin] = []
    for idx in range(bins):
        bucket = grouped.get(idx, [])
        if not bucket:
            continue
        lower = idx * width
        upper = lower + width
        avg_pred = sum(item.probability for item in bucket) / len(bucket)
        avg_outcome = sum(item.outcome for item in bucket) / len(bucket)
        output.append(
            CalibrationBin(
                lower=lower,
                upper=upper,
                count=len(bucket),
                avg_pred=avg_pred,
                avg_outcome=avg_outcome,
            )
        )
    return output


def fit_temperature_scaling(
    train_scores: list[ScoreRecord],
    validation_scores: list[ScoreRecord],
    domain: str,
    horizon: str,
) -> float:
    train_filtered = [s for s in train_scores if s.domain == domain and s.horizon == horizon]
    valid_filtered = [s for s in validation_scores if s.domain == domain and s.horizon == horizon]
    if not train_filtered or not valid_filtered:
        return 1.0

    best_alpha = 1.0
    best_loss = float("inf")
    for i in range(5, 31):
        alpha = i / 10.0
        loss = 0.0
        for row in valid_filtered:
            scaled = min(max(row.probability ** (1.0 / alpha), 1e-6), 1 - 1e-6)
            loss += brier_score(scaled, row.outcome)
        avg_loss = loss / len(valid_filtered)
        if avg_loss < best_loss:
            best_loss = avg_loss
            best_alpha = alpha
    return best_alpha


def strict_time_split(
    scores: list[ScoreRecord], split_idx: int
) -> tuple[list[ScoreRecord], list[ScoreRecord]]:
    sorted_scores = sorted(scores, key=lambda s: s.resolved_at)
    if split_idx <= 0 or split_idx >= len(sorted_scores):
        raise ValueError("split_idx must create non-empty past/future partitions")
    return sorted_scores[:split_idx], sorted_scores[split_idx:]


def monitoring_alerts(
    recent_scores: list[ScoreRecord], baseline_brier: float, brier_spike_threshold: float = 0.05
) -> MonitoringAlert:
    if not recent_scores:
        return MonitoringAlert(False, "insufficient_data", 1.0)
    current = sum(row.brier for row in recent_scores) / len(recent_scores)
    degradation = current - baseline_brier
    if degradation > brier_spike_threshold:
        shrink = max(0.6, 1.0 - degradation)
        return MonitoringAlert(True, "brier_spike", shrink)
    return MonitoringAlert(False, "stable", 1.0)


def freeze_protocol(current_alpha: float, alert: MonitoringAlert) -> tuple[bool, float]:
    if not alert.should_freeze:
        return False, current_alpha
    return True, current_alpha * alert.suggested_alpha_shrink
