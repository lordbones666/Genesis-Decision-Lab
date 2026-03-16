from __future__ import annotations

from collections import defaultdict, deque


def propagate_event_shock(
    base_probabilities: dict[str, float],
    edges: list[tuple[str, str, float]],
    shocked_event: str,
    shock_delta: float,
    max_depth: int = 3,
) -> dict[str, float]:
    adjacency: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for src, dst, weight in edges:
        adjacency[src].append((dst, weight))

    updated = dict(base_probabilities)
    updated[shocked_event] = min(max(updated.get(shocked_event, 0.5) + shock_delta, 0.0), 1.0)
    queue: deque[tuple[str, float, int]] = deque([(shocked_event, shock_delta, 0)])

    while queue:
        node, delta, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for nxt, weight in adjacency.get(node, []):
            propagated = delta * weight
            updated[nxt] = min(max(updated.get(nxt, 0.5) + propagated, 0.0), 1.0)
            queue.append((nxt, propagated, depth + 1))
    return updated
