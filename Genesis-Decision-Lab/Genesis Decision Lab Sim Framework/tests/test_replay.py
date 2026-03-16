from datetime import datetime, timezone
from pathlib import Path

from forecasting_engine.ledger import EvidenceLedger, ForecastLedger, replay_forecast
from forecasting_engine.models import ForecastSnapshot, StructuredEvidenceObject


def test_golden_replay_fixture(tmp_path: Path) -> None:
    forecast_ledger = ForecastLedger(tmp_path / "forecast.jsonl")
    evidence_ledger = EvidenceLedger(tmp_path / "evidence.jsonl")

    seo = StructuredEvidenceObject(
        event_id="evt1",
        question_id="C1",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        category="security",
        direction=1,
        magnitude="small",
        claim_type="event",
        source_ids=["sr1"],
        source_tier="tier_1",
    )
    evidence_ledger.append_evidence(seo, source_ids=["sr1"])

    snapshot_baseline = ForecastSnapshot(
        question_id="C1",
        as_of=datetime(2026, 1, 2, tzinfo=timezone.utc),
        probability=0.6,
        logodds=0.405,
        pre_logodds=0.0,
        delta_logodds=0.405,
        config_version="weights-v1",
        evidence_ids=["evt1"],
        ablation_label="baseline",
    )
    snapshot_regime = ForecastSnapshot(
        question_id="C1",
        as_of=datetime(2026, 1, 2, tzinfo=timezone.utc),
        probability=0.62,
        logodds=0.49,
        pre_logodds=0.0,
        delta_logodds=0.49,
        config_version="weights-v1",
        evidence_ids=["evt1"],
        ablation_label="+regime",
    )
    forecast_ledger.append_forecast(snapshot_baseline)
    forecast_ledger.append_forecast(snapshot_regime)

    replayed = replay_forecast(
        forecast_ledger,
        evidence_ledger,
        "C1",
        "2026-01-02T00:00:00+00:00",
        ablation_label="baseline",
    )
    assert replayed["forecast"]["probability"] == 0.6
    assert replayed["evidence"][0]["event_id"] == "evt1"
