# Abacus Analytica

## Decision Lab seed (first slice)

This repository now includes a minimal Decision Lab seed that preserves the forecasting/simulation architecture while adding:

- an external self-model manifest (`config/self_model_manifest.yaml`)
- a thin world-model bridge over existing simulation/predictive modules (`src/forecasting_engine/orchestration/world_model_bridge.py`)
- policy-driven uncertainty routing (`src/forecasting_engine/orchestration/uncertainty_router.py`)
- a minimal orchestration runner for one NL task path (`src/forecasting_engine/orchestration/runner.py`)

Start here:

1. Operator note and end-to-end flow: `docs/decision_lab_seed.md`
2. Manifest loader contract: `src/forecasting_engine/orchestration/tool_manifest.py`
3. Runner entry point: `src/forecasting_engine/orchestration/runner.py`
4. Tests:
   - `tests/test_tool_manifest.py`
   - `tests/test_world_model_bridge.py`
   - `tests/test_uncertainty_router.py`
   - `tests/test_orchestration_runner.py`
