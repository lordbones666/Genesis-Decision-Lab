from forecasting_engine.orchestration.uncertainty_router import (
    UncertaintyPolicy,
    UncertaintyRoutingInput,
    route_uncertainty,
)


def test_uncertainty_router_returns_valid() -> None:
    decision = route_uncertainty(
        UncertaintyRoutingInput(
            tool_name="domain_simulation",
            required_inputs=["simulator_name", "inputs"],
            provided_inputs={"simulator_name", "inputs"},
            confidence=0.85,
            stale_evidence_days=7,
            simulator_name="macro_system",
        ),
        policy=UncertaintyPolicy(allowed_simulators={"macro_system"}),
    )

    assert decision.status == "valid"


def test_uncertainty_router_returns_partial_for_missing_inputs() -> None:
    decision = route_uncertainty(
        UncertaintyRoutingInput(
            tool_name="monte_carlo_paths",
            required_inputs=["initial_value", "threshold_value", "mu", "sigma"],
            provided_inputs={"initial_value", "mu", "sigma"},
            confidence=0.72,
        ),
        policy=UncertaintyPolicy(),
    )

    assert decision.status == "partial"
    assert any(reason.startswith("missing_inputs") for reason in decision.reasons)


def test_uncertainty_router_returns_out_of_domain_for_low_confidence() -> None:
    decision = route_uncertainty(
        UncertaintyRoutingInput(
            tool_name="bayesian_update",
            required_inputs=["prior", "evidence"],
            provided_inputs={"prior", "evidence"},
            confidence=0.2,
        ),
        policy=UncertaintyPolicy(),
    )

    assert decision.status == "out_of_domain"


def test_uncertainty_router_flags_unsupported_simulator() -> None:
    decision = route_uncertainty(
        UncertaintyRoutingInput(
            tool_name="domain_simulation",
            required_inputs=["simulator_name", "inputs"],
            provided_inputs={"simulator_name", "inputs"},
            confidence=0.7,
            simulator_name="unknown_sim",
        ),
        policy=UncertaintyPolicy(allowed_simulators={"macro_system"}),
    )

    assert decision.status == "partial"
    assert "unsupported_simulator:unknown_sim" in decision.reasons
