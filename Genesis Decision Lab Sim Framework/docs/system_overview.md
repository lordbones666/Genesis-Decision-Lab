# System Overview

This repository implements a reproducible forecasting engine with the execution order:

1. Question definition and gating (`question_gate`, `validate_question_object`)
2. Source acquisition and snapshotting (`web_search_fetch` -> SRs)
3. Evidence structuring (`sr_to_seo`) and deduplication (`dedupe_cluster`)
4. Routing to question IDs (`route_to_questions`)
5. Probability updates (`update_logodds`) with optional regime and ablation layers
6. Ledger persistence and replay (`EvidenceLedger`, `ForecastLedger`, `replay_forecast`)
7. Scoring, calibration, and monitoring (`brier_score`, `fit_temperature_scaling`, `monitoring_alerts`)

Web search note:
- GPT/tooling performs retrieval.
- `web_search_fetch` is an adapter that normalizes retrieved results into replayable Source Records.

Machine-readable discovery aids:
- `repo_manifest.json`
- `file_manifest.json`

Additional methodology pack:
- `docs/specs/` (12-topic Abacus forecasting playbook)

- `docs/specs/13_extension_roadmap_geopolitical_macro.md` (numeric-range, tactical, structural, and macro bridge modules)
- `docs/specs/14_universal_tetlock_module_v1.md` (universal question-to-dashboard superforecasting layer)
- `docs/specs/15_high_leverage_modules_pack.md` (question compiler, numeric, timeseries, regime, dependency, decay, source memory, backtests, surprise triggers, valuation)


## Decision Lab Phase 2
The system now includes formal scenario compilation, simulation run provenance, portfolio risk summaries, regime/state summaries, and deterministic rerun triage scaffolding.
