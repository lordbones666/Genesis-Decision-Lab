from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from forecasting_engine.orchestration.contracts import WorldModelResult


@dataclass(frozen=True)
class QuestionObject:
    prompt: str
    problem_family: str
    target_domain: str
    actors: list[str]
    horizon_days: int
    requested_outputs: list[str]
    comparison_mode: str
    hypothesis_hints: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    uncertainty_posture: str = "balanced"
    discriminating_signal_interest: bool = True
    sensitivity_test_variables: list[str] = field(default_factory=list)
    rerun_from_trace_id: str | None = None


@dataclass(frozen=True)
class EvidenceHandoff:
    focus_summary: str
    prior_context: list[str]
    evidence_themes: list[str]
    corpus_filters: dict[str, str]
    relevant_document_ids: list[str] = field(default_factory=list)
    relevant_source_ids: list[str] = field(default_factory=list)
    operator_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AnalysisRequest:
    question: QuestionObject
    evidence_handoff: EvidenceHandoff
    task: str
    as_of: datetime
    payload: dict[str, Any]


@dataclass(frozen=True)
class AnalysisResultBundle:
    question: QuestionObject
    evidence_handoff_summary: dict[str, Any]
    selected_method: str
    world_model_result: WorldModelResult | None
    result_payload: dict[str, Any]
    assumptions: list[str]
    uncertainty_status: str
    traces: dict[str, Any]
    linked_hypotheses: list[str]
    discriminating_signals: list[str]
    possible_next_moves: list[str]
    decision_relevance: str
    trace_id: str | None
    ledger_refs: list[str]
    warnings: list[str]
    operator_review_flags: list[str]
