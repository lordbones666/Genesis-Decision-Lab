from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CausalEdge:
    parent: str
    child: str
    weight: float


@dataclass(frozen=True)
class StructuralCausalResult:
    downstream_effects: dict[str, float]
    intervention_forecast: float
    causal_sensitivity: dict[str, float]


def run_structural_causal_graph(
    baseline: dict[str, float],
    edges: list[CausalEdge],
    intervention_node: str,
    intervention_delta: float,
    steps: int = 2,
) -> StructuralCausalResult:
    state = dict(baseline)
    state[intervention_node] = float(state.get(intervention_node, 0.0)) + intervention_delta

    for _ in range(max(1, steps)):
        updates = dict(state)
        for edge in edges:
            parent_value = state.get(edge.parent, 0.0)
            updates[edge.child] = updates.get(edge.child, baseline.get(edge.child, 0.0)) + (
                parent_value * edge.weight
            )
        state = updates

    downstream = {
        node: state.get(node, 0.0) - baseline.get(node, 0.0)
        for node in set(state) | set(baseline)
        if node != intervention_node
    }
    sensitivity: dict[str, float] = {}
    norm = max(abs(intervention_delta), 1e-6)
    for edge in edges:
        sensitivity[f"{edge.parent}->{edge.child}"] = abs(edge.weight) / norm

    return StructuralCausalResult(
        downstream_effects=dict(sorted(downstream.items())),
        intervention_forecast=state.get(intervention_node, 0.0),
        causal_sensitivity=dict(sorted(sensitivity.items())),
    )
