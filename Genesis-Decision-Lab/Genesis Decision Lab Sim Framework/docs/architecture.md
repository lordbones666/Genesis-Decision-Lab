# Forecasting Engine V1.1 Architecture

Pipeline: `question_gate -> SR ingest+snapshot -> SEO extraction -> dedupe cluster -> route -> log-odds update -> optional regime/MC ablations -> ledgers -> scoring/calibration -> monitoring/freeze`.

Layer split:
- `policies/*`: pure, side-effect-free algorithm modules (deterministic math/decision logic).
- `pipeline.py`: orchestration and data-flow wiring.
- `ledger.py`: append-only persistence and replay.

Core stores:
- Evidence ledger (SEO + provenance + correction links)
- Forecast ledger (pre/post log-odds + config versions + reversal metadata + artifacts)
- Score ledger (outcomes, Brier, calibration params)

Replay uses timestamped ledger rows plus source snapshots (`content_hash`, `excerpt`, optional `archive_pointer`) to produce audit-ready reconstruction.

Governance:
- Config change control requires version bump + rationale + expected impact + replay diff.
- Drift monitoring can trigger freeze protocol and aggressiveness reduction.


## Simulation Layer (additive)

A new `src/forecasting_engine/simulation/` package extends existing policies/extensions with explicit simulation contracts, deterministic seeded execution, and bridge adapters to evidence + ledger pathways. This layer is additive and does not replace the baseline pipeline.


## Decision Lab Phase 2 Additions
Phase 2 layers are additive: `scenario/*`, `portfolio/*`, `dashboard/*`, and `automation/*` plus explicit ledgers for scenarios, simulation runs, and portfolios. The orchestration-policy split remains unchanged.
