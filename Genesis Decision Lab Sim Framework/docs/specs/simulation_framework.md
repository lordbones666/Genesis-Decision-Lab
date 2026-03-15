# Simulation Framework Spec (Additive v1)

## Objectives

1. Preserve existing forecasting architecture.
2. Add reusable Bayesian / Markov / Monte Carlo simulation foundations.
3. Add domain simulators and bridges for forecast integration.
4. Keep runs replay-safe and seed-controlled.

## Core Contracts

`SimulationContext` carries scenario metadata and reproducibility controls.

`SimulationOutput` is a normalized container:

- `state`: latent/structural state values.
- `metrics`: forecast-relevant outcomes.
- `assumptions`: interpretable modeling assumptions.
- `artifacts`: optional diagnostics.

## Core Engines

### Bayesian

- Prior probability + evidence likelihood ratios.
- Tier weight multipliers.
- Optional evidence aging via half-life decay.
- Returns posterior + confidence interval metadata.

### Markov

- Explicit state list + full transition matrix.
- Path simulation with seeded PRNG.
- State occupancy outputs for downstream risk estimates.
- HMM scaffold included for future filtering inference.

### Monte Carlo

- Generic seeded path simulation with jump-diffusion option.
- Distribution envelope (`p10/p50/p90`) and threshold-hit probability.
- Legacy bridge to existing market-path policy logic.

## Domain Simulators

Included initial domains:

- macro system
- conflict escalation
- crisis cascade
- financial contagion
- supply chain
- sanctions trade
- commodity flows
- alliance deterrence
- institutional stability
- migration unrest
- election transition
- social contagion

Each simulator is intentionally reduced-form, deterministic except explicit seeded transitions, and exposes assumptions.

## Integration

- `simulation_to_evidence` maps simulation outputs into SEO-compatible payloads.
- `SimulationLedger` writes append-only artifacts for replay inspection.
- Existing engine layers remain untouched; simulation integration is additive.
