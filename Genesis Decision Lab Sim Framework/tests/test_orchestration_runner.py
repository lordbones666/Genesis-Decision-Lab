from datetime import datetime

from forecasting_engine.orchestration.runner import run_decision_lab_task


def test_runner_routes_simulation_for_monte_carlo_task() -> None:
    response = run_decision_lab_task(
        task_text="Estimate threshold probability with Monte Carlo",
        as_of=datetime(2026, 3, 14),
        payload={
            "initial_value": 100.0,
            "threshold_value": 105.0,
            "mu": 0.08,
            "sigma": 0.15,
            "steps": 8,
            "runs": 30,
            "seed": 11,
        },
    )

    assert response.routing_decision == "simulate"
    assert response.world_model_result is not None
    assert response.world_model_result.tool_name == "monte_carlo_paths"
    assert response.used_manifest_version == "decision-lab-seed.v1"


def test_runner_refuses_unsupported_task() -> None:
    response = run_decision_lab_task(
        task_text="Summarize repository TODOs",
        as_of=datetime(2026, 3, 14),
        payload={},
    )

    assert response.routing_decision == "refuse"
    assert response.world_model_result is None
    assert response.known_unknowns
