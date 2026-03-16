from __future__ import annotations

from dataclasses import asdict
from typing import Any

from forecasting_engine.orchestration.analysis_contracts import (
    AnalysisRequest,
    AnalysisResultBundle,
    EvidenceHandoff,
    QuestionObject,
)
from forecasting_engine.orchestration.hypothesis_manager import InMemoryHypothesisManager
from forecasting_engine.orchestration.report_builder import DecisionReport, build_report
from forecasting_engine.orchestration.runner import run_decision_lab_task


def build_question_object(
    prompt: str,
    *,
    problem_family: str,
    target_domain: str,
    actors: list[str],
    horizon_days: int,
    requested_outputs: list[str],
    comparison_mode: str = "single_path",
    hypothesis_hints: list[str] | None = None,
    missing_information: list[str] | None = None,
    uncertainty_posture: str = "balanced",
    discriminating_signal_interest: bool = True,
    sensitivity_test_variables: list[str] | None = None,
    rerun_from_trace_id: str | None = None,
) -> QuestionObject:
    return QuestionObject(
        prompt=prompt,
        problem_family=problem_family,
        target_domain=target_domain,
        actors=actors,
        horizon_days=horizon_days,
        requested_outputs=requested_outputs,
        comparison_mode=comparison_mode,
        hypothesis_hints=hypothesis_hints or [],
        missing_information=missing_information or [],
        uncertainty_posture=uncertainty_posture,
        discriminating_signal_interest=discriminating_signal_interest,
        sensitivity_test_variables=sensitivity_test_variables or [],
        rerun_from_trace_id=rerun_from_trace_id,
    )


def build_evidence_handoff(
    focus_summary: str,
    *,
    prior_context: list[str] | None = None,
    evidence_themes: list[str] | None = None,
    corpus_filters: dict[str, str] | None = None,
    relevant_document_ids: list[str] | None = None,
    relevant_source_ids: list[str] | None = None,
    operator_notes: list[str] | None = None,
) -> EvidenceHandoff:
    return EvidenceHandoff(
        focus_summary=focus_summary,
        prior_context=prior_context or [],
        evidence_themes=evidence_themes or [],
        corpus_filters=corpus_filters or {},
        relevant_document_ids=relevant_document_ids or [],
        relevant_source_ids=relevant_source_ids or [],
        operator_notes=operator_notes or [],
    )


def run_analysis(
    request: AnalysisRequest,
    hypothesis_manager: InMemoryHypothesisManager | None = None,
) -> AnalysisResultBundle:
    effective_payload = dict(request.payload)
    effective_payload.setdefault("analysis_context", _to_context(request.evidence_handoff))
    if request.question.rerun_from_trace_id:
        effective_payload.setdefault("rerun_from_trace_id", request.question.rerun_from_trace_id)

    response = run_decision_lab_task(
        task_text=request.task,
        payload=effective_payload,
        as_of=request.as_of,
    )
    result = response.world_model_result
    known = (
        hypothesis_manager.list_for_problem(request.question.problem_family)
        if hypothesis_manager
        else []
    )

    linked_hypotheses = sorted(
        set(request.question.hypothesis_hints)
        | {item.hypothesis_id for item in known if item.current_weight >= 0.4}
    )
    discriminating_signals = _discriminating_signals(request.question, known)
    trace_id = None if result is None else str(result.traces.get("trace_id"))

    return AnalysisResultBundle(
        question=request.question,
        evidence_handoff_summary=asdict(request.evidence_handoff),
        selected_method="none" if result is None else result.tool_name,
        world_model_result=result,
        result_payload={} if result is None else result.output,
        assumptions=[] if result is None else result.assumptions,
        uncertainty_status="out_of_domain" if result is None else result.uncertainty_status,
        traces={} if result is None else result.traces,
        linked_hypotheses=linked_hypotheses,
        discriminating_signals=discriminating_signals,
        possible_next_moves=_next_moves(result, request, linked_hypotheses),
        decision_relevance=_decision_relevance(result, request.question.requested_outputs),
        trace_id=trace_id,
        ledger_refs=_ledger_refs(result),
        warnings=_warnings(result, request.evidence_handoff),
        operator_review_flags=_operator_flags(result, request.question, request.evidence_handoff),
    )


def get_report(bundle: AnalysisResultBundle) -> DecisionReport:
    return build_report(bundle)


def _next_moves(
    result: Any,
    request: AnalysisRequest,
    linked_hypotheses: list[str],
) -> list[str]:
    if result is None:
        return ["Provide a structured payload with required fields for a supported tool."]
    if result.out_of_domain:
        return [
            "Inspect failure reason and re-run with complete required inputs.",
            "Use corpus filters or document IDs to tighten evidence scope.",
        ]
    moves = list(result.recommended_next_checks)
    if linked_hypotheses:
        moves.append("Review competing hypotheses and update support/contradiction evidence links.")
    if request.question.sensitivity_test_variables:
        variables = ", ".join(request.question.sensitivity_test_variables)
        moves.append(f"Run sensitivity sweeps for variables: {variables}.")
    return moves


def _decision_relevance(result: Any, requested_outputs: list[str]) -> str:
    if result is None or result.out_of_domain:
        return "low"
    if result.uncertainty_status == "partial":
        return "medium"
    return "high" if requested_outputs else "medium"


def _ledger_refs(result: Any) -> list[str]:
    if result is None:
        return []
    seed = result.traces.get("trace_id")
    if not isinstance(seed, str):
        return []
    return [f"ledger://analysis/{seed}"]


def _warnings(result: Any, handoff: EvidenceHandoff) -> list[str]:
    warnings: list[str] = []
    if result is None or result.out_of_domain:
        warnings.append("analysis_out_of_domain")
    if not handoff.relevant_document_ids and not handoff.relevant_source_ids:
        warnings.append("evidence_handoff_without_explicit_document_refs")
    return warnings


def _operator_flags(result: Any, question: QuestionObject, handoff: EvidenceHandoff) -> list[str]:
    flags: list[str] = []
    if result is not None and result.uncertainty_status == "partial":
        flags.append("partial_domain_review")
    if question.comparison_mode != "single_path":
        flags.append("comparison_mode_requested")
    if len(handoff.operator_notes) > 0:
        flags.append("operator_notes_present")
    return flags


def _to_context(handoff: EvidenceHandoff) -> dict[str, Any]:
    return {
        "focus_summary": handoff.focus_summary,
        "evidence_themes": handoff.evidence_themes,
        "corpus_filters": handoff.corpus_filters,
        "document_ids": handoff.relevant_document_ids,
        "source_ids": handoff.relevant_source_ids,
        "operator_notes": handoff.operator_notes,
    }


def _discriminating_signals(
    question: QuestionObject,
    known_hypotheses: list[Any],
) -> list[str]:
    if not question.discriminating_signal_interest:
        return []
    collected = {
        signal
        for hypothesis in known_hypotheses
        for signal in getattr(hypothesis, "discriminating_signals", [])
    }
    return sorted(collected)
