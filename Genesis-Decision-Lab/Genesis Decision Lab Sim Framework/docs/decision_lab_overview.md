# Decision Lab Overview (Phase 2)

## Scope
Phase 2 extends the existing simulation framework with scenario formalization, provenance hardening, ledgers, portfolio structure, regime/state summary outputs, and rerun triage scaffolding.

## Phase 2A audit summary
- `simulation/contracts.py` provided deterministic core contracts but lacked an explicit simulation run provenance contract.
- `simulation/core/orchestrator.py` cleanly delegated execution to registry entries and remained suitable for extension without rewrite.
- `simulation/bridges/ledger_bridge.py` persisted outputs but did not produce replay-grade run IDs, evidence snapshot hashes, or regime snapshot linkage.
- `simulation/bridges/forecast_bridge.py` generated simulation evidence correctly but had no explicit run identifier link for downstream audit chains.

## What Phase 2 adds
- First-class scenario contracts/compiler/templates/registry.
- Explicit ledgers for scenarios, simulation runs, and forecast portfolios.
- Deterministic run record generation with evidence snapshot hashing.
- Portfolio contracts + exposure/correlation summaries.
- Regime/state summary objects for operator-facing Decision Lab status.
- Rerun triage classification scaffolding.

## Intentionally deferred
- UI/dashboard front-end work.
- Advanced portfolio optimization and allocation engines.
- Scheduler/worker automation runtime.
