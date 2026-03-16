from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from forecasting_engine.orchestration.hypothesis_contracts import HypothesisRecord, HypothesisStatus


class InMemoryHypothesisManager:
    def __init__(self) -> None:
        self._records: dict[str, HypothesisRecord] = {}

    def register(self, hypothesis: HypothesisRecord) -> HypothesisRecord:
        self._records[hypothesis.hypothesis_id] = hypothesis
        return hypothesis

    def get(self, hypothesis_id: str) -> HypothesisRecord | None:
        return self._records.get(hypothesis_id)

    def list_for_problem(self, problem_family: str) -> list[HypothesisRecord]:
        return sorted(
            [h for h in self._records.values() if h.problem_family == problem_family],
            key=lambda item: item.current_weight,
            reverse=True,
        )

    def attach_evidence(
        self,
        hypothesis_id: str,
        *,
        support_ids: list[str] | None = None,
        contradict_ids: list[str] | None = None,
    ) -> HypothesisRecord:
        existing = self._require(hypothesis_id)
        updated = replace(
            existing,
            supporting_evidence_ids=sorted(
                set(existing.supporting_evidence_ids) | set(support_ids or [])
            ),
            contradicting_evidence_ids=sorted(
                set(existing.contradicting_evidence_ids) | set(contradict_ids or [])
            ),
            updated_at=datetime.now(UTC),
        )
        self._records[hypothesis_id] = self._reweight(updated)
        return self._records[hypothesis_id]

    def update_status(self, hypothesis_id: str, status: HypothesisStatus) -> HypothesisRecord:
        existing = self._require(hypothesis_id)
        updated = replace(existing, status=status, updated_at=datetime.now(UTC))
        self._records[hypothesis_id] = updated
        return updated

    def link_models(self, hypothesis_id: str, model_names: list[str]) -> HypothesisRecord:
        existing = self._require(hypothesis_id)
        updated = replace(
            existing,
            linked_models=sorted(set(existing.linked_models) | set(model_names)),
            updated_at=datetime.now(UTC),
        )
        self._records[hypothesis_id] = updated
        return updated

    def _reweight(self, record: HypothesisRecord) -> HypothesisRecord:
        support = len(record.supporting_evidence_ids)
        contradict = len(record.contradicting_evidence_ids)
        if support + contradict == 0:
            return record
        weight = max(0.0, min(1.0, 0.5 + 0.12 * support - 0.16 * contradict))
        if contradict > support:
            status: HypothesisStatus = "weakened"
        elif support > contradict:
            status = "active"
        else:
            status = record.status
        return replace(record, current_weight=weight, status=status, updated_at=datetime.now(UTC))

    def _require(self, hypothesis_id: str) -> HypothesisRecord:
        record = self._records.get(hypothesis_id)
        if record is None:
            raise KeyError(f"unknown hypothesis_id: {hypothesis_id}")
        return record
