from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkEdge:
    source: str
    target: str
    weight: float


@dataclass(frozen=True)
class ContagionResult:
    node_states: dict[str, float]
    cascade_likelihood: float
    critical_nodes: list[str]


def propagate_contagion(
    node_states: dict[str, float],
    edges: list[NetworkEdge],
    trigger_node: str,
    trigger_delta: float,
    threshold: float = 0.55,
    iterations: int = 3,
) -> ContagionResult:
    state = dict(node_states)
    state[trigger_node] = min(max(state.get(trigger_node, 0.0) + trigger_delta, 0.0), 1.0)

    for _ in range(max(1, iterations)):
        next_state = dict(state)
        for edge in edges:
            source_level = state.get(edge.source, 0.0)
            transmitted = source_level * edge.weight
            next_state[edge.target] = min(
                max(next_state.get(edge.target, 0.0) + transmitted, 0.0), 1.0
            )
        state = next_state

    impacted = [name for name, value in state.items() if value >= threshold]
    likelihood = len(impacted) / max(len(state), 1)
    ranked = sorted(state.items(), key=lambda item: item[1], reverse=True)
    critical = [name for name, _ in ranked[: min(3, len(ranked))]]

    return ContagionResult(
        node_states=dict(sorted(state.items())),
        cascade_likelihood=likelihood,
        critical_nodes=critical,
    )
