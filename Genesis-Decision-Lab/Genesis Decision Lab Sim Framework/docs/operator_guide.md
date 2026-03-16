# End-to-End System Usage Guide

## 1) Define and gate the question
1. Create Question Object payload.
2. Run `question_gate(payload)`.
3. If gate fails, revise resolver, binary criteria, and time window.
4. Validate with `validate_question_object`.

## 2) Acquire sources and snapshot evidence
1. Run `web_search_fetch(query, search_results)` to create Source Records.
2. Ensure SR fields include `url`, `retrieved_at`, `publisher`, `content_hash`, and `excerpt`.
3. Store SRs.

## 3) Build structured evidence
1. Convert SRs via `sr_to_seo(...)`.
2. Use `claim_type="correction"` + `correction_of_event_id` for retractions/corrections.
3. Dedupe with `dedupe_cluster`.
4. Route with `route_to_questions`.

## 4) Update forecasts and run ablations
1. Apply `update_logodds(...)` with config weights and optional historical deltas.
2. Apply optional `regime_update(...)`.
3. For K4-style market path, run `monte_carlo(...)`.
4. Produce default ablations via `run_ablation_forecasts(...)`:
   - baseline
   - +regime
   - +regime+mc

## 5) Persist and replay
1. Append SEO rows to EvidenceLedger.
2. Append snapshots to ForecastLedger.
3. Use `replay_forecast(...)` for timestamp replay.

## 6) Score, calibrate, and monitor
1. Score with `score_forecasts` and `brier_score`.
2. Time split with `strict_time_split`.
3. Fit alpha via `fit_temperature_scaling`.
4. Run `monitoring_alerts` and `freeze_protocol` to detect drift and auto-shrink aggressiveness.

## 7) Config change governance
Before changing weights/regime config:
- bump version,
- record rationale,
- document expected impact,
- attach fixture replay diff,
- validate with `validate_change_control`.
