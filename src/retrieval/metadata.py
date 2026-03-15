"""Metadata and provenance normalization for retrieval chunks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .chunking import Chunk


@dataclass(frozen=True)
class SourceRecord:
    """Canonical metadata for one ingested source file."""

    source_id: str
    title: str
    path: str
    source_type: str
    timestamp: str
    canonical: bool
    provenance_note: str


def _timestamp_for(path: Path) -> str:
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return modified.isoformat()


def build_source_record(
    path: Path, source_type: str = "document", canonical: bool = True
) -> SourceRecord:
    """Create normalized source metadata from a file path."""

    return SourceRecord(
        source_id=path.stem,
        title=path.name,
        path=str(path),
        source_type=source_type,
        timestamp=_timestamp_for(path),
        canonical=canonical,
        provenance_note="ingested_from_filesystem",
    )


def build_chunk_metadata(source: SourceRecord, chunk: Chunk) -> dict[str, object]:
    """Return metadata payload attached to retrieval items."""

    return {
        "title": source.title,
        "path": source.path,
        "source_type": source.source_type,
        "timestamp": source.timestamp,
        "canonical": source.canonical,
        "chunk_order": chunk.order,
        "start_char": chunk.start_char,
        "end_char": chunk.end_char,
    }


def build_provenance(source: SourceRecord, chunk: Chunk) -> dict[str, object]:
    """Return provenance payload for retrieval transparency."""

    return {
        "source_id": source.source_id,
        "chunk_id": chunk.chunk_id,
        "provenance_note": source.provenance_note,
        "location": {
            "path": source.path,
            "chunk_order": chunk.order,
            "start_char": chunk.start_char,
            "end_char": chunk.end_char,
        },
        "timestamp": source.timestamp,
    }
