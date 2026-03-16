from datetime import datetime

from forecasting_engine.orchestration.analysis_adapter import (
    build_evidence_handoff,
    build_question_object,
    get_report,
    run_analysis,
)
from forecasting_engine.orchestration.analysis_contracts import AnalysisRequest


def test_report_builder_returns_structured_decision_report() -> None:
    question = build_question_object(
        "Estimate hidden state",
        problem_family="hidden_state",
        target_domain="macro",
        actors=["policy_maker"],
        horizon_days=45,
        requested_outputs=["state_probabilities"],
    )
    handoff = build_evidence_handoff(
        "focus on inflation and growth",
        evidence_themes=["inflation", "pmi"],
        corpus_filters={"region": "US"},
        relevant_document_ids=["doc-1"],
    )
    request = AnalysisRequest(
        question=question,
        evidence_handoff=handoff,
        task="hidden state inference for macro regime",
        as_of=datetime(2026, 3, 16),
        payload={"indicators": {"vix": 32.0, "inflation": 3.9, "pmi": 48.0}},
    )

    bundle = run_analysis(request)
    report = get_report(bundle)

    assert report.headline
    assert report.selected_methods
    assert "focus" in report.evidence_summary
    assert report.trace_references.get("trace_id")
