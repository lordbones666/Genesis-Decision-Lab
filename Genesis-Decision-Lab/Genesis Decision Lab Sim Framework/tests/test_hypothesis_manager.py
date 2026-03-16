from forecasting_engine.orchestration.hypothesis_contracts import HypothesisRecord
from forecasting_engine.orchestration.hypothesis_manager import InMemoryHypothesisManager


def test_hypothesis_lifecycle_register_attach_and_status() -> None:
    manager = InMemoryHypothesisManager()
    record = HypothesisRecord(
        hypothesis_id="h-1",
        title="Liquidity spiral",
        description="Funding stress amplifies cascade risk",
        problem_family="network_contagion",
        assumptions=["short-term funding remains constrained"],
        falsifiers=["funding spreads normalize"],
        discriminating_signals=["repo_spread_widening"],
        next_information_needed=["counterparty net exposure"],
    )

    manager.register(record)
    updated = manager.attach_evidence("h-1", support_ids=["ev-1"], contradict_ids=["ev-2"])
    assert updated.hypothesis_id == "h-1"
    assert "ev-1" in updated.supporting_evidence_ids
    assert "ev-2" in updated.contradicting_evidence_ids

    weakened = manager.update_status("h-1", "weakened")
    assert weakened.status == "weakened"


def test_hypothesis_list_for_problem_sorted_by_weight() -> None:
    manager = InMemoryHypothesisManager()
    manager.register(
        HypothesisRecord(
            hypothesis_id="h-a",
            title="A",
            description="A",
            problem_family="macro",
            assumptions=[],
            current_weight=0.9,
        )
    )
    manager.register(
        HypothesisRecord(
            hypothesis_id="h-b",
            title="B",
            description="B",
            problem_family="macro",
            assumptions=[],
            current_weight=0.4,
        )
    )

    ranked = manager.list_for_problem("macro")
    assert ranked[0].hypothesis_id == "h-a"
