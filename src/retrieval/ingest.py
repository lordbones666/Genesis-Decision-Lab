"""Ingestion pipeline from local files to retrieval-ready records."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .chunking import chunk_text
from .metadata import build_chunk_metadata, build_provenance, build_source_record


@dataclass(frozen=True)
class IngestedChunk:
    """Retrieval-ready record emitted by ingestion."""

    id: str
    source_id: str
    text: str
    metadata: dict[str, object]
    provenance: dict[str, object]


@dataclass(frozen=True)
class IngestionConfig:
    """Small ingestion settings for repeatable chunking."""

    chunk_size: int = 500
    overlap: int = 50
    source_type: str = "document"
    canonical: bool = True


def _base_dir(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    resolved = [path.resolve() for path in paths]
    return Path(os.path.commonpath([str(path) for path in resolved]))


def ingest_paths(
    paths: list[Path], config: IngestionConfig | None = None
) -> list[IngestedChunk]:
    """Ingest a curated corpus and emit deterministic chunk records."""

    if not paths:
        return []

    cfg = config or IngestionConfig()
    records: list[IngestedChunk] = []
    common_base_dir = _base_dir(paths)

    for path in sorted(paths):
        text = path.read_text(encoding="utf-8")
        source = build_source_record(
            path,
            source_type=cfg.source_type,
            canonical=cfg.canonical,
            base_dir=common_base_dir,
        )
        chunks = chunk_text(
            source.source_id, text, chunk_size=cfg.chunk_size, overlap=cfg.overlap
        )
        for chunk in chunks:
            records.append(
                IngestedChunk(
                    id=chunk.chunk_id,
                    source_id=source.source_id,
                    text=chunk.text,
                    metadata=build_chunk_metadata(source, chunk),
                    provenance=build_provenance(source, chunk),
                )
            )

    return records
