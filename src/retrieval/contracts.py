"""Typed retrieval contracts for Decision Lab retrieval substrate."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RetrievalRequest:
    """Narrow retrieval request consumed by upstream callers."""

    query: str
    filters: dict[str, Any] | None = None
    top_k: int = 5

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("query must be non-empty")
        if self.top_k <= 0:
            raise ValueError("top_k must be greater than zero")


@dataclass(frozen=True)
class RetrievalResult:
    """One ranked retrieval hit with metadata and provenance."""

    id: str
    source_id: str
    text: str
    score: float
    metadata: dict[str, Any]
    provenance: dict[str, Any]


@dataclass(frozen=True)
class RetrievalResponse:
    """Wrapper around ranked retrieval hits."""

    query: str
    results: list[RetrievalResult] = field(default_factory=list)


def result_to_dict(result: RetrievalResult) -> dict[str, Any]:
    """Serialize a result for external consumers."""

    return {
        "id": result.id,
        "source_id": result.source_id,
        "text": result.text,
        "score": result.score,
        "metadata": result.metadata,
        "provenance": result.provenance,
    }
