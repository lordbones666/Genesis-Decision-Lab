from __future__ import annotations

import random

from forecasting_engine.simulation.contracts import MarkovSimulationResult, MarkovStep


class MarkovChain:
    def __init__(self, states: list[str], transition_matrix: dict[str, dict[str, float]]) -> None:
        self.states = states
        self.transition_matrix = transition_matrix
        self._validate()

    def _validate(self) -> None:
        state_set = set(self.states)
        for state in self.states:
            row = self.transition_matrix.get(state)
            if row is None:
                raise ValueError(f"Missing transition row for state={state}")
            row_total = sum(row.values())
            if abs(row_total - 1.0) > 1e-9:
                raise ValueError(f"Transition probabilities for {state} must sum to 1.0")
            if set(row.keys()) != state_set:
                raise ValueError(f"Transition row for {state} must include all states")

    def next_state(self, current_state: str, rng: random.Random) -> str:
        row = self.transition_matrix[current_state]
        draw = rng.random()
        cumulative = 0.0
        for state in self.states:
            cumulative += row[state]
            if draw <= cumulative:
                return state
        return self.states[-1]

    def simulate_path(self, start_state: str, steps: int, seed: int) -> MarkovSimulationResult:
        if start_state not in self.transition_matrix:
            raise ValueError(f"Unknown start_state={start_state}")
        rng = random.Random(seed)
        counts = {state: 0 for state in self.states}
        path: list[MarkovStep] = []
        state = start_state
        for idx in range(steps):
            path.append(MarkovStep(step=idx, state=state))
            counts[state] += 1
            state = self.next_state(state, rng)
        return MarkovSimulationResult(start_state=start_state, path=path, state_counts=counts)


class HiddenMarkovScaffold:
    """Lightweight scaffold to support future HMM filtering extensions."""

    def __init__(self, latent_states: list[str], emissions: dict[str, dict[str, float]]) -> None:
        self.latent_states = latent_states
        self.emissions = emissions

    def emission_probability(self, state: str, observation: str) -> float:
        return float(self.emissions.get(state, {}).get(observation, 0.0))
