# Decision Lab Seed (Phase 1)

## Scope

This seed adds a minimal Decision Lab path without replacing deterministic forecasting core logic.

## Components

- `config/self_model_manifest.yaml`: external self-model manifest with routing cues, required inputs, failure modes, verification notes, and tool-specific uncertainty policies.
- `src/forecasting_engine/orchestration/tool_manifest.py`: manifest loader with structural and semantic validation.
- `src/forecasting_engine/orchestration/world_model_bridge.py`: manifest-aligned callable adapter over existing modules.
- `src/forecasting_engine/orchestration/uncertainty_router.py`: policy-driven `valid` / `partial` / `out_of_domain` routing.
- `src/forecasting_engine/orchestration/contracts.py`: typed request/response contracts.
- `src/forecasting_engine/orchestration/runner.py`: single orchestration entry point for one NL task path.

## Bridge coverage

The world-model bridge wraps existing substrate modules:

1. `simulation.core.bayesian.bayesian_update`
2. `simulation.core.monte_carlo.run_paths`
3. `simulation.core.orchestrator.SimulationOrchestrator.run`

No simulator internals were rewritten.

## End-to-end path example

1. Task arrives: "Estimate threshold probability with Monte Carlo."
2. `runner.run_decision_lab_task(...)` classifies task and reads `config/self_model_manifest.yaml`.
3. It routes to `monte_carlo_paths` (simulation-only path in this seed).
4. `WorldModelBridge.call(...)` validates manifest/tool/inputs and executes existing simulation.
5. `route_uncertainty(...)` applies tool policy and returns `valid`, `partial`, or `out_of_domain`.
6. Response includes summary, assumptions, structured output, uncertainty status, and reproducible traces.

## Operator request/response examples

### 1) Bayesian update

Request payload:

```python
{
  "prior": 0.4,
  "evidence": [
    {"evidence_id": "ev-1", "likelihood_ratio": 1.5, "weight": 1.0},
    {"evidence_id": "ev-2", "likelihood_ratio": 0.9, "weight": 0.6}
  ]
}
```

Response highlights:

- `output.posterior`
- `output.confidence_interval`
- `uncertainty_status`
- `traces.trace_id`

### 2) Monte Carlo paths

Request payload:

```python
{
  "initial_value": 100.0,
  "threshold_value": 105.0,
  "mu": 0.08,
  "sigma": 0.15,
  "steps": 16,
  "runs": 80,
  "seed": 11
}
```

Response highlights:

- `output.threshold_hit_probability`
- `output.quantiles`
- `traces.seed`
- `traces.config_version`

### 3) Domain simulation

Request payload:

```python
{
  "simulator_name": "macro_system",
  "inputs": {
    "global_growth": -0.2,
    "inflation_shock": 0.3,
    "policy_rate": 0.12,
    "energy_disruption": 0.25
  },
  "scenario_id": "seed-e2e",
  "horizon_steps": 6,
  "seed": 17
}
```

Response highlights:

- `output.state`
- `output.metrics`
- `output.context.seed`
- `traces.simulator_name`

## What was done well already

- Existing forecasting/simulation substrate is preserved.
- Bridge wraps existing modules instead of rebuilding engines.
- External self-model manifest drives tool-level contracts.
- Uncertainty status is explicit rather than implicit.

## Operations checklist

- [ ] Validate manifest structure and semantics via `tests/test_tool_manifest.py`.
- [ ] Validate bridge contract behavior and failure states.
- [ ] Validate uncertainty routing reason codes and statuses.
- [ ] Validate runner end-to-end routing path.
- [ ] Log seeds/config versions/trace IDs for reproducibility.
