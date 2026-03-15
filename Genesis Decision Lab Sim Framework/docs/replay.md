# Replay Procedure

1. Load `forecast_ledger.jsonl` and locate record by `question_id` and `as_of`.
2. If multiple ablation snapshots share the same timestamp, select by `ablation_label`.
3. Pull `evidence_ids` from forecast row.
4. Load evidence rows matching those IDs.
5. Verify config versions from forecast row.
6. Recompute update and compare probability equality.
