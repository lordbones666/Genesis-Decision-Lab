# Genesis Decision Lab — Retrieval Substrate Seed

This repository hosts the retrieval substrate workstream for the Decision Lab seed.

## Scope and relationship to Decision Lab

The retrieval substrate provides:
- ingestion
- chunking
- metadata and provenance
- indexing and retrieval
- retrieval evaluation

It is retrieval infrastructure for evidence access.
It is **not** simulation logic, world-model logic, or orchestration policy.

## Retrieval contract

The substrate exposes a narrow retrieval function:

```python
retrieve(query: str, filters: dict | None = None, top_k: int = 5) -> list[dict]
```

Each returned result has:
- `id`
- `source_id`
- `text`
- `score`
- `metadata`
- `provenance`

## Seed components

- `src/retrieval/contracts.py`: typed request/response contracts.
- `src/retrieval/chunking.py`: deterministic chunking with stable chunk IDs.
- `src/retrieval/metadata.py`: metadata/provenance normalization.
- `src/retrieval/ingest.py`: curated-corpus ingestion to retrieval-ready records.
- `src/retrieval/index.py`: minimal retrieval index with metadata filtering.
- `tests/test_retrieval_eval.py`: retrieval regression checks.

For operator notes, see `docs/retrieval_seed.md`.
