"""Simple deterministic chunking helpers."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    """Stable chunk unit emitted by ingestion."""

    chunk_id: str
    source_id: str
    order: int
    start_char: int
    end_char: int
    text: str


def chunk_text(
    source_id: str, text: str, chunk_size: int = 500, overlap: int = 50
) -> list[Chunk]:
    """Chunk text with stable IDs based on source and span."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    stripped = text.strip()
    if not stripped:
        return []

    chunks: list[Chunk] = []
    cursor = 0
    order = 0
    length = len(text)
    step = chunk_size - overlap

    while cursor < length:
        end = min(cursor + chunk_size, length)
        segment = text[cursor:end].strip()
        if segment:
            span = f"{source_id}:{cursor}:{end}".encode("utf-8")
            chunk_id = hashlib.sha1(span).hexdigest()[:16]
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    source_id=source_id,
                    order=order,
                    start_char=cursor,
                    end_char=end,
                    text=segment,
                )
            )
            order += 1
        if end == length:
            break
        cursor += step

    return chunks
