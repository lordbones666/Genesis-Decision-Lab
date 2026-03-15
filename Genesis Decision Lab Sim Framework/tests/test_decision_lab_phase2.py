from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from forecasting_engine.automation.rerun_triage import (
    TRIAGE_EVIDENCE_ONLY,
    TRIAGE_OPERATOR_REVIEW_REQUIRED,
    TRIAGE_RERUN_REQUIRED,
    TRIAGE_SCENARIO_AFFECTING,
    classify_update,
)
from forecasting_engine.config_loader import (
    load_automation_defaults,
    load_portfolio_defaults,
    load_scenario_defaults,
)
from forecasting_engine.dashboard.regime_state import build_regime_state_summary
from forecasting_engine.dashboard.summary_views import assemble_summary_view
from forecasting_engine.portfolio.correlation import compute_scenario_overlap
from forecasting_engine.portfolio.forecast_portfolio import build_forecast_portfolio
from forecasting_engine.scenario.compiler import compile_scenario
from forecasting_engine.scenario.registry import ScenarioRegistry
from forecasting_engine.simulation.bridges.ledger_bridge import build_run_record
from forecasting_engine.simulation.contracts import SimulationContext
from forecasting_engine.simulation.core.orchestrator import SimulationOrchestrator
from ledger.forecast_portfolio_ledger import ForecastPortfolioLedger
from ledger.scenario_ledger import ScenarioLedger
from ledger.simulation_run_ledger import SimulationRunLedger


def test_scenario_compiler_determinism_and_registry() -> None:
    first = compile_scenario(
        template_id="macro_stress",
        label="Macro 2026",
        linked_evidence_ids=["ev-2", "ev-1"],
        state_assumptions={"inflation": 4.1, "growth": 0.5, "policy_rate": 4.8},
        regime_assumptions={"risk_off": 0.7},
        confidence_level=0.62,
        uncertainty_note="Policy pass-through lag uncertain.",
        config_version="scenario-templates-v1",
    )
    second = compile_scenario(
        template_id="macro_stress",
        label="Macro 2026",
        linked_evidence_ids=["ev-1", "ev-2"],
        state_assumptions={"inflation": 4.1, "growth": 0.5, "policy_rate": 4.8},
        regime_assumptions={"risk_off": 0.7},
        confidence_level=0.62,
        uncertainty_note="Policy pass-through lag uncertain.",
        config_version="scenario-templates-v1",
    )
    assert first.scenario_id == second.scenario_id
    registry = ScenarioRegistry()
    registry.register(first)
    assert registry.get(first.scenario_id).template_version == "v1"


def test_simulation_run_record_provenance_and_ledger(tmp_path: Path) -> None:
    orchestrator = SimulationOrchestrator()
    context = SimulationContext(
        scenario_id="scenario-a",
        as_of=datetime(2026, 2, 1, tzinfo=timezone.utc),
        horizon_steps=8,
        seed=11,
        config_version="simulation-framework-v1",
    )
    output = orchestrator.run("macro_system", context, {"inflation": 3.4, "growth": 1.3})
    record = build_run_record(
        output=output,
        simulator_version="macro_system@v1",
        evidence_snapshot={"ids": ["ev-1", "ev-2"]},
        regime_snapshot={"risk_off": 0.6, "risk_on": 0.4},
    )
    assert record.run_id
    assert record.evidence_snapshot_hash

    run_ledger = SimulationRunLedger(tmp_path / "simulation_runs.jsonl")
    run_ledger.append_run(record)
    rows = run_ledger.read_all()
    assert rows[0]["scenario_id"] == "scenario-a"


def test_scenario_and_portfolio_ledgers(tmp_path: Path) -> None:
    scenario = compile_scenario(
        template_id="conflict_spillover",
        label="Spillover risk",
        linked_evidence_ids=["ev-11"],
        state_assumptions={"trigger_intensity": 0.7, "deterrence_strength": 0.3},
        regime_assumptions={"risk_off": 0.8},
        confidence_level=0.55,
        uncertainty_note="Escalation threshold uncertain.",
        config_version="scenario-templates-v1",
    )
    scenario_ledger = ScenarioLedger(tmp_path / "scenario.jsonl")
    scenario_ledger.append_scenario(scenario)
    assert scenario_ledger.read_all()[0]["scenario_id"] == scenario.scenario_id

    overlap = compute_scenario_overlap(
        {"f1": {scenario.scenario_id}, "f2": {scenario.scenario_id, "x"}}
    )
    portfolio = build_forecast_portfolio(
        portfolio_id="pf-1",
        forecast_ids=["f1", "f2"],
        question_ids=["q1", "q2"],
        scenario_ids=[scenario.scenario_id],
        forecast_weights={"f1": 0.6, "f2": 0.4},
        scenario_overlap=overlap,
        correlation_pairs={"f1|f2": 0.7},
        regime_sensitivity={"risk_off": 0.8},
        assumptions=["Linear stress weighting"],
    )
    portfolio_ledger = ForecastPortfolioLedger(tmp_path / "portfolio.jsonl")
    portfolio_ledger.append_portfolio(portfolio)
    assert portfolio_ledger.read_all()[0]["portfolio_id"] == "pf-1"


def test_regime_summary_and_decision_view_deterministic() -> None:
    summary = build_regime_state_summary(
        as_of="2026-02-01T00:00:00+00:00",
        regime_probabilities={"risk_off": 0.6, "risk_on": 0.4},
        top_drivers=["credit_spreads", "shipping_delay"],
        previous_regime_probabilities={"risk_off": 0.5, "risk_on": 0.5},
    )
    view = assemble_summary_view(summary, ["scn-1"], ["pf-1"], ["f-9", "f-8"])
    assert view.regime.recent_changes["risk_off"] == 0.1
    assert view.impacted_forecasts == ("f-8", "f-9")


def test_rerun_triage_categories() -> None:
    assert (
        classify_update(
            {"evidence_ids": ["e1"], "scenario_id": "s1"},
            {"evidence_ids": ["e1", "e2"], "scenario_id": "s1"},
        ).category
        == TRIAGE_EVIDENCE_ONLY
    )
    assert (
        classify_update(
            {"scenario_id": "s1", "trigger_set": ["a"]},
            {"scenario_id": "s1", "trigger_set": ["a", "b"]},
        ).category
        == TRIAGE_SCENARIO_AFFECTING
    )
    assert (
        classify_update(
            {"manual_override": "off"},
            {"manual_override": "on"},
        ).category
        == TRIAGE_OPERATOR_REVIEW_REQUIRED
    )
    assert (
        classify_update(
            {"seed": 1, "config_version": "v1"},
            {"seed": 2, "config_version": "v1"},
        ).category
        == TRIAGE_RERUN_REQUIRED
    )


def test_new_defaults_and_schemas_present() -> None:
    assert load_scenario_defaults(Path("config"))["templates"]["version"] == "scenario-templates-v1"
    assert load_portfolio_defaults(Path("config"))["defaults"]["version"] == "portfolio-defaults-v1"
    assert load_automation_defaults(Path("config"))["triage"]["version"] == "triage-default-v1"

    for schema_path in [
        Path("schemas/scenario/scenario.schema.json"),
        Path("schemas/portfolio/portfolio.schema.json"),
        Path("schemas/automation/triage.schema.json"),
    ]:
        with schema_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        assert payload["title"]
