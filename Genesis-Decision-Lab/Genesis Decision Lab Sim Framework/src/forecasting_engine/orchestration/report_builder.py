from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from forecasting_engine.orchestration.analysis_contracts import AnalysisResultBundle


@dataclass(frozen=True)
class DecisionReport:
    headline: str
    question_summary: str
    selected_methods: list[str]
    evidence_summary: dict[str, Any]
    assumptions: list[str]
    uncertainty_status: str
    linked_hypotheses: list[str]
    discriminating_signals: list[str]
    decision_relevance: str
    suggested_next_moves: list[str]
    trace_references: dict[str, Any] = field(default_factory=dict)
    ledger_references: list[str] = field(default_factory=list)
    human_summary: str | None = None


def build_report(bundle: AnalysisResultBundle) -> DecisionReport:
    method = bundle.selected_method or "unrouted"
    output_keys = sorted(bundle.result_payload.keys())
    headline = f"{method}: {bundle.uncertainty_status} result for {bundle.question.target_domain}"
    evidence_summary = {
        "focus": bundle.evidence_handoff_summary.get("focus_summary", ""),
        "themes": bundle.evidence_handoff_summary.get("evidence_themes", []),
        "corpus_filters": bundle.evidence_handoff_summary.get("corpus_filters", {}),
        "document_ids": bundle.evidence_handoff_summary.get("relevant_document_ids", []),
        "source_ids": bundle.evidence_handoff_summary.get("relevant_source_ids", []),
        "result_fields": output_keys,
    }
    human_summary = (
        f"Method {method} returned {bundle.uncertainty_status} with relevance "
        f"{bundle.decision_relevance}. Key outputs: {', '.join(output_keys) or 'none'}."
    )
    return DecisionReport(
        headline=headline,
        question_summary=bundle.question.prompt,
        selected_methods=[method],
        evidence_summary=evidence_summary,
        assumptions=bundle.assumptions,
        uncertainty_status=bundle.uncertainty_status,
        linked_hypotheses=bundle.linked_hypotheses,
        discriminating_signals=bundle.discriminating_signals,
        decision_relevance=bundle.decision_relevance,
        suggested_next_moves=bundle.possible_next_moves,
        trace_references={"trace_id": bundle.trace_id, **bundle.traces},
        ledger_references=bundle.ledger_refs,
        human_summary=human_summary,
    )
