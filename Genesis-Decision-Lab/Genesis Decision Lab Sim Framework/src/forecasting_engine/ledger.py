from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from forecasting_engine.models import ForecastSnapshot, ScoreRecord, StructuredEvidenceObject


class JsonlLedger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, payload: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, default=_encode_dt) + "\n")

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
        return rows


def _encode_dt(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


class EvidenceLedger(JsonlLedger):
    def append_evidence(self, seo: StructuredEvidenceObject, source_ids: list[str]) -> None:
        payload = asdict(seo)
        payload["source_ids"] = source_ids
        self.append(payload)


class ForecastLedger(JsonlLedger):
    def append_forecast(self, snapshot: ForecastSnapshot) -> None:
        self.append(asdict(snapshot))


class ScoreLedger(JsonlLedger):
    def append_score(self, score: ScoreRecord) -> None:
        self.append(asdict(score))


def replay_forecast(
    forecast_ledger: ForecastLedger,
    evidence_ledger: EvidenceLedger,
    question_id: str,
    as_of_iso: str,
    ablation_label: str | None = None,
) -> dict[str, Any]:
    forecasts = [
        item
        for item in forecast_ledger.read_all()
        if item["question_id"] == question_id and item["as_of"] == as_of_iso
    ]
    if ablation_label is not None:
        forecasts = [item for item in forecasts if item.get("ablation_label") == ablation_label]
    if not forecasts:
        msg = (
            f"No forecast found for question={question_id} as_of={as_of_iso}"
            if ablation_label is None
            else (
                f"No forecast found for question={question_id} as_of={as_of_iso} "
                f"ablation_label={ablation_label}"
            )
        )
        raise KeyError(msg)
    forecast = forecasts[-1]
    evidence_ids = set(forecast.get("evidence_ids", []))
    evidence = [item for item in evidence_ledger.read_all() if item["event_id"] in evidence_ids]
    return {"forecast": forecast, "evidence": evidence}
