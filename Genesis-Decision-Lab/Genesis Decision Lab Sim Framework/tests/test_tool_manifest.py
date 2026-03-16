from pathlib import Path

import pytest

from forecasting_engine.orchestration.tool_manifest import load_self_model_manifest


def test_load_self_model_manifest_has_expected_tools() -> None:
    manifest = load_self_model_manifest("config/self_model_manifest.yaml")

    assert manifest.version == "decision-lab-seed.v1"
    assert set(manifest.tools) == {
        "bayesian_update",
        "monte_carlo_paths",
        "domain_simulation",
        "structural_causal_graph",
        "network_contagion",
        "actor_response",
        "hazard_failure",
        "scenario_tree_generator",
        "hidden_state_estimator",
        "uncertainty_decomposition",
        "value_of_information",
        "model_arbitration",
    }
    assert manifest.routing_defaults["require_uncertainty_router"] is True
    assert set(manifest.uncertainty_policies) == set(manifest.tools)


def test_tool_entries_include_required_contract_sections() -> None:
    manifest = load_self_model_manifest("config/self_model_manifest.yaml")

    bayesian = manifest.tools["bayesian_update"]
    assert "prior" in bayesian.required_inputs
    assert "posterior" in bayesian.output_shape
    assert bayesian.failure_modes
    assert bayesian.verification_notes


def test_manifest_rejects_unknown_routing_action(tmp_path: Path) -> None:
    invalid_manifest = tmp_path / "invalid_manifest.yaml"
    invalid_manifest.write_text(
        """
version: "v1"
routing_defaults:
  unsupported_task_action: "unknown"
uncertainty_policies:
  bayesian_update: {}
tools:
  - name: "bayesian_update"
    purpose: "x"
    when_to_use: ["a"]
    when_not_to_use: ["b"]
    required_inputs: ["prior", "evidence"]
    output_shape:
      prior: "float"
      posterior: "float"
      effective_likelihood_ratio: "float"
      confidence_interval: "list[float]"
      explanation: "dict[str, float|str]"
    failure_modes: ["f"]
    verification_notes: ["v"]
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unsupported_task_action"):
        load_self_model_manifest(invalid_manifest)


def test_manifest_rejects_duplicate_tool_names(tmp_path: Path) -> None:
    duplicate_manifest = tmp_path / "duplicate_manifest.yaml"
    duplicate_manifest.write_text(
        """
version: "v1"
routing_defaults:
  unsupported_task_action: "refuse"
uncertainty_policies:
  bayesian_update: {}
tools:
  - name: "bayesian_update"
    purpose: "x"
    when_to_use: ["a"]
    when_not_to_use: ["b"]
    required_inputs: ["prior", "evidence"]
    output_shape:
      prior: "float"
      posterior: "float"
      effective_likelihood_ratio: "float"
      confidence_interval: "list[float]"
      explanation: "dict[str, float|str]"
    failure_modes: ["f"]
    verification_notes: ["v"]
  - name: "bayesian_update"
    purpose: "y"
    when_to_use: ["a"]
    when_not_to_use: ["b"]
    required_inputs: ["prior", "evidence"]
    output_shape:
      prior: "float"
      posterior: "float"
      effective_likelihood_ratio: "float"
      confidence_interval: "list[float]"
      explanation: "dict[str, float|str]"
    failure_modes: ["f"]
    verification_notes: ["v"]
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate tool name"):
        load_self_model_manifest(duplicate_manifest)
