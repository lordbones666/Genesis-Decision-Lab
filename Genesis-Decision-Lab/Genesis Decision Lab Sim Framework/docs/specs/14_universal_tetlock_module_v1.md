# Universal Tetlock Module v1

Implements a reusable superforecasting layer that is domain-agnostic:
- question factory + good-question gate
- base-rate selection (outside view first)
- decomposition helpers (AND chain, noisy-OR)
- structured evidence and status labeling
- log-odds updates with capped deltas
- causal graph propagation and event-tree simulation
- sentiment layer (SPS/NHI) + sentiment-to-delta mapping
- universal domain resolver map + default live dashboard panels

Module location:
- `src/forecasting_engine/extensions/tetlock_module.py`
