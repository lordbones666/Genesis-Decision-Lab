# Simulation Framework Overview

## Phase 1: Existing Simulation Substrate Map

The repository already had simulation-capable components that remain preserved and are now wrapped by the new simulation layer:

- Monte Carlo GBM barrier logic in `policies/market_path.py`.
- Regime signal extraction in `extensions/regime_detector.py` and macro plumbing in `extensions/market_macro.py`.
- State/dependency propagation in `extensions/dependency_graph.py` and `extensions/event_network.py`.
- Range/threshold support in `extensions/numeric_thresholds.py` and `extensions/range_forecaster.py`.
- Evaluation/backtest assets in `extensions/backtest_harness.py` and `evaluation.py`.

## Additive Simulation Layer

New package: `src/forecasting_engine/simulation/`.

- `core/`: Bayesian updates, Markov transitions (and HMM scaffold), and generalized Monte Carlo.
- `domains/`: domain interpretable simulators (macro, conflict, cascade, contagion, supply chain, etc.).
- `bridges/`: conversion into structured evidence and JSONL simulation ledger artifacts.
- `contracts.py`: typed contracts for simulation context, outputs, and model result objects.
- `registry.py`: simulator registration and default simulator catalog.

## Replay / Determinism Contract

Every run captures:

- explicit `seed`
- `scenario_id`
- `config_version`
- `as_of`
- simulator name

All stochastic engines route through explicit seeded PRNG flows.

## Change Report (module-level)

- `core/bayesian.py`: likelihood-ratio Bayesian update with tier weighting and optional recency decay.
- `core/markov.py`: finite-state Markov chain path simulation and HMM extension scaffold.
- `core/monte_carlo.py`: reusable jump-diffusion path runner; legacy market-path compatibility bridge.
- `domains/*`: interpretable first-pass simulators with explicit assumptions and structured outputs.
- `bridges/forecast_bridge.py`: simulation output to SEO conversion for pipeline ingestion.
- `bridges/ledger_bridge.py`: append-only simulation ledger integration.

## Known Scaffold Limits

Domain modules are intentionally reduced-form and not full structural models; they expose explicit assumptions and parameters for iterative hardening.


## Phase 2 Provenance Integration
Simulation outputs are now expected to map into a simulation run record with deterministic run identifiers, evidence snapshot hash, regime snapshot, and simulator/config version metadata.
