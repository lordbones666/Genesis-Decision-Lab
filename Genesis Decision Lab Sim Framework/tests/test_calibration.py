from datetime import datetime, timedelta, timezone

from forecasting_engine.evaluation import strict_time_split
from forecasting_engine.models import ScoreRecord


def test_time_split_enforces_past_vs_future() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    scores = [
        ScoreRecord("Q1", base + timedelta(days=i), i % 2, 0.5, 0.25, "energy", "1m")
        for i in range(6)
    ]
    train, valid = strict_time_split(scores, split_idx=4)
    assert max(t.resolved_at for t in train) < min(v.resolved_at for v in valid)
