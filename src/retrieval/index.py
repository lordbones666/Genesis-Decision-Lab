"""Minimal in-memory retrieval index with provenance-backed results."""

from __future__ import annotations

import math
import re
from collections import Counter

from .contracts import RetrievalRequest, RetrievalResponse, RetrievalResult
from .ingest import IngestedChunk

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_RE.findall(text)]


class RetrievalIndex:
    """Small lexical index to support deterministic retrieval evaluation."""

    def __init__(self, records: list[IngestedChunk]) -> None:
        self.records = records
        self._doc_freq: Counter[str] = Counter()
        self._tf: dict[str, Counter[str]] = {}
        self._build()

    def _build(self) -> None:
        for record in self.records:
            tf = Counter(_tokens(record.text))
            self._tf[record.id] = tf
            self._doc_freq.update(tf.keys())

    def retrieve(
        self, query: str, filters: dict[str, object] | None = None, top_k: int = 5
    ) -> list[dict[str, object]]:
        """Narrow retrieval interface for Decision Lab consumers."""

        request = RetrievalRequest(query=query, filters=filters, top_k=top_k)
        response = self._retrieve(request)
        return [
            {
                "id": result.id,
                "source_id": result.source_id,
                "text": result.text,
                "score": result.score,
                "metadata": result.metadata,
                "provenance": result.provenance,
            }
            for result in response.results
        ]

    def _retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        query_tf = Counter(_tokens(request.query))
        ranked: list[RetrievalResult] = []
        corpus_size = max(len(self.records), 1)

        for record in self.records:
            if not self._match_filters(record, request.filters):
                continue
            score = 0.0
            doc_tf = self._tf.get(record.id, Counter())
            for token, q_count in query_tf.items():
                if token not in doc_tf:
                    continue
                idf = math.log((corpus_size + 1) / (1 + self._doc_freq[token])) + 1.0
                score += float(doc_tf[token] * q_count) * idf
            if score > 0:
                ranked.append(
                    RetrievalResult(
                        id=record.id,
                        source_id=record.source_id,
                        text=record.text,
                        score=score,
                        metadata=record.metadata,
                        provenance=record.provenance,
                    )
                )

        ranked.sort(key=lambda item: item.score, reverse=True)
        return RetrievalResponse(query=request.query, results=ranked[: request.top_k])

    @staticmethod
    def _match_filters(
        record: IngestedChunk, filters: dict[str, object] | None
    ) -> bool:
        if not filters:
            return True
        for key, expected in filters.items():
            if (
                record.metadata.get(key) != expected
                and getattr(record, key, None) != expected
            ):
                return False
        return True
