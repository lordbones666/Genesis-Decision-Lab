# Retrieval Substrate Seed

This retrieval layer is evidence infrastructure for Decision Lab. It ingests source documents,
chunks them deterministically, preserves provenance, and returns ranked evidence results.
It does **not** perform world-model reasoning, simulation, or orchestration policy.

## End-to-end path

1. Ingest curated files with `ingest_paths` from `src/retrieval/ingest.py`.
2. Create `RetrievalIndex(records)` from `src/retrieval/index.py`.
3. Query with:

```python
results = index.retrieve(query="regime transition", filters={"canonical": True}, top_k=5)
```

Each result contains:
- `id`
- `source_id`
- `text`
- `score`
- `metadata`
- `provenance`

## Provenance guarantees

Every retrieval hit includes source/path/chunk location via `provenance`, including:
- source identifier
- chunk identifier
- path
- chunk order and character span
- ingestion timestamp
- provenance note

## Evaluation seed

`tests/test_retrieval_eval.py` provides a small golden query set for retrieval regression checks,
including known-item retrieval and metadata-filter behavior.
