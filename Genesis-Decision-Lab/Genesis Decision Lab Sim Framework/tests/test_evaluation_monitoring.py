from datetime import datetime, timedelta, timezone

from forecasting_engine.evaluation import freeze_protocol, monitoring_alerts
from forecasting_engine.models import ScoreRecord


def test_monitoring_alert_triggers_freeze() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    scores = [
        ScoreRecord("Q1", base + timedelta(days=i), 0, 0.9, 0.81, "energy", "1m") for i in range(5)
    ]
    alert = monitoring_alerts(scores, baseline_brier=0.2)
    freeze, alpha = freeze_protocol(1.0, alert)
    assert freeze
    assert alpha < 1.0
