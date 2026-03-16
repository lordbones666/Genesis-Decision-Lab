from datetime import datetime

from forecasting_engine.orchestration.analysis_adapter import (
    build_evidence_handoff,
    build_question_object,
    run_analysis,
)
from forecasting_engine.orchestration.analysis_contracts import AnalysisRequest
from forecasting_engine.orchestration.hypothesis_contracts import HypothesisRecord
from forecasting_engine.orchestration.hypothesis_manager import InMemoryHypothesisManager


def test_build_question_and_handoff() -> None:
    question = build_question_object(
        "Assess contagion risk",
        problem_family="network_contagion",
        target_domain="financial",
        actors=["bank_a", "bank_b"],
        horizon_days=30,
        requested_outputs=["cascade_likelihood"],
        comparison_mode="branch_compare",
        hypothesis_hints=["liquidity_shock"],
        missing_information=["counterparty concentration"],
        uncertainty_posture="conservative",
        sensitivity_test_variables=["threshold", "edge_weights"],
        rerun_from_trace_id="wm-prior-123",
    )
    handoff = build_evidence_handoff(
        "focus on banking stress",
        prior_context=["prior run showed medium risk"],
        evidence_themes=["liquidity", "credit spreads"],
        corpus_filters={"region": "global"},
        relevant_document_ids=["doc-a"],
        relevant_source_ids=["src-a"],
        operator_notes=["watch sovereign spillover"],
    )

    assert question.problem_family == "network_contagion"
    assert handoff.corpus_filters["region"] == "global"
    assert handoff.relevant_document_ids == ["doc-a"]


def test_run_analysis_returns_structured_bundle_with_hypotheses() -> None:
    question = build_question_object(
        "Assess contagion risk",
        problem_family="network_contagion",
        target_domain="financial",
        actors=["bank_a", "bank_b"],
        horizon_days=30,
        requested_outputs=["cascade_likelihood"],
    )
    handoff = build_evidence_handoff("focus on banking stress", corpus_filters={"region": "global"})

    manager = InMemoryHypothesisManager()
    manager.register(
        HypothesisRecord(
            hypothesis_id="h-liquidity",
            title="Liquidity spiral",
            description="Funding stress amplifies cascade",
            problem_family="network_contagion",
            assumptions=["funding dries up"],
            discriminating_signals=["repo_spread_widening"],
            current_weight=0.8,
            status="active",
        )
    )

    request = AnalysisRequest(
        question=question,
        evidence_handoff=handoff,
        task="simulate network contagion cascade",
        as_of=datetime(2026, 3, 16),
        payload={
            "node_states": {"bank_a": 0.8, "bank_b": 0.2, "bank_c": 0.1},
            "edges": [
                {"source": "bank_a", "target": "bank_b", "weight": 0.5},
                {"source": "bank_b", "target": "bank_c", "weight": 0.4},
            ],
            "trigger_node": "bank_a",
            "trigger_delta": 0.1,
        },
    )

    bundle = run_analysis(request, hypothesis_manager=manager)

    assert bundle.world_model_result is not None
    assert bundle.decision_relevance in {"medium", "high"}
    assert bundle.possible_next_moves
    assert bundle.evidence_handoff_summary["corpus_filters"]["region"] == "global"
    assert "h-liquidity" in bundle.linked_hypotheses
    assert "repo_spread_widening" in bundle.discriminating_signals
