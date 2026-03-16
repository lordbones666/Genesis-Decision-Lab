from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from forecasting_engine.config_loader import load_simulation_defaults
from forecasting_engine.simulation.bridges.forecast_bridge import simulation_to_evidence
from forecasting_engine.simulation.bridges.ledger_bridge import SimulationLedger
from forecasting_engine.simulation.contracts import BayesianEvidence, SimulationContext
from forecasting_engine.simulation.core.bayesian import bayesian_update
from forecasting_engine.simulation.core.markov import MarkovChain
from forecasting_engine.simulation.core.monte_carlo import MonteCarloConfig, run_paths
from forecasting_engine.simulation.core.orchestrator import SimulationOrchestrator


def test_bayesian_update_increases_with_supportive_evidence() -> None:
    result = bayesian_update(
        prior=0.4,
        evidence=[
            BayesianEvidence(
                evidence_id="e1", likelihood_ratio=2.0, source_tier="tier1", weight=1.0
            ),
            BayesianEvidence(
                evidence_id="e2", likelihood_ratio=1.4, source_tier="tier2", weight=0.7
            ),
        ],
        as_of=datetime.now(timezone.utc),
        tier_weights={"tier1": 1.2, "tier2": 1.0, "default": 0.8},
    )
    assert result.posterior > result.prior
    assert 0.0 <= result.confidence_interval[0] <= result.confidence_interval[1] <= 1.0


def test_markov_simulation_deterministic_with_seed() -> None:
    chain = MarkovChain(
        states=["stable", "crisis"],
        transition_matrix={
            "stable": {"stable": 0.8, "crisis": 0.2},
            "crisis": {"stable": 0.3, "crisis": 0.7},
        },
    )
    p1 = chain.simulate_path("stable", steps=12, seed=42)
    p2 = chain.simulate_path("stable", steps=12, seed=42)
    assert [step.state for step in p1.path] == [step.state for step in p2.path]


def test_monte_carlo_reproducibility() -> None:
    cfg = MonteCarloConfig(steps=30, runs=200, jump_probability=0.01, jump_mean=0.0, jump_std=0.02)
    summary_1, _ = run_paths(100.0, 108.0, 0.08, 0.2, seed=99, cfg=cfg)
    summary_2, _ = run_paths(100.0, 108.0, 0.08, 0.2, seed=99, cfg=cfg)
    assert summary_1.threshold_hit_probability == summary_2.threshold_hit_probability
    assert summary_1.quantiles == summary_2.quantiles


def test_orchestrator_and_bridge_integration() -> None:
    orchestrator = SimulationOrchestrator()
    context = SimulationContext(
        scenario_id="scenario-1",
        as_of=datetime(2026, 1, 1, tzinfo=timezone.utc),
        horizon_steps=10,
        seed=7,
        config_version="simulation-framework-v1",
    )
    output = orchestrator.run("conflict_escalation", context, {"trigger_intensity": 0.4})
    seo = simulation_to_evidence(output, question_id="q-conflict", category="geopolitics")
    assert seo.claim_type == "simulation"
    assert seo.metadata["seed"] == 7


def test_simulation_ledger_persistence(tmp_path: Path) -> None:
    orchestrator = SimulationOrchestrator()
    context = SimulationContext(
        scenario_id="scenario-ledger",
        as_of=datetime(2026, 1, 1, tzinfo=timezone.utc),
        horizon_steps=5,
        seed=8,
        config_version="simulation-framework-v1",
    )
    output = orchestrator.run("macro_system", context, {"inflation": 3.1, "growth": 1.7})
    ledger = SimulationLedger(tmp_path / "simulation.jsonl")
    ledger.append_simulation(output)
    rows = ledger.read_all()
    assert len(rows) == 1
    assert rows[0]["scenario_id"] == "scenario-ledger"


def test_simulation_configs_and_schemas_exist() -> None:
    defaults = load_simulation_defaults(Path("config"))
    assert defaults["framework"]["version"] == "simulation-framework-v1"
    schema_path = Path("schemas/simulation/framework.schema.json")
    with schema_path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    assert schema["title"] == "Simulation Framework Config"


def test_domain_simulator_sanity() -> None:
    orchestrator = SimulationOrchestrator()
    context = SimulationContext(
        scenario_id="scenario-domain",
        as_of=datetime(2026, 1, 1, tzinfo=timezone.utc),
        horizon_steps=8,
        seed=4,
        config_version="simulation-framework-v1",
    )
    for name in ["supply_chain", "financial_contagion", "social_contagion"]:
        output = orchestrator.run(name, context, {})
        assert output.simulator == name
        assert output.metrics
