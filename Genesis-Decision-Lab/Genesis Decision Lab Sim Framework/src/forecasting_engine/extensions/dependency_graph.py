from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyEdge:
    source: str
    target: str
    weight: float


def propagate_dependencies(
    probabilities: dict[str, float],
    edges: list[DependencyEdge],
    changed_node: str,
    delta: float,
) -> dict[str, float]:
    output = dict(probabilities)
    output[changed_node] = min(max(output.get(changed_node, 0.5) + delta, 0.0), 1.0)
    for edge in edges:
        if edge.source != changed_node:
            continue
        output[edge.target] = min(max(output.get(edge.target, 0.5) + delta * edge.weight, 0.0), 1.0)
    return output
