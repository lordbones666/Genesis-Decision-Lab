from pathlib import Path
from typing import Any

from retrieval.index import RetrievalIndex
from retrieval.ingest import IngestionConfig, ingest_paths


def _build_seed_index(tmp_path: Path) -> RetrievalIndex:
    corpus = tmp_path / "corpus"
    corpus.mkdir()

    (corpus / "canonical_policy.md").write_text(
        "Canonical policy guidance for sanctions and trade monitoring.",
        encoding="utf-8",
    )
    (corpus / "draft_note.md").write_text(
        "Draft note on social media narrative risk and monitoring.", encoding="utf-8"
    )
    (corpus / "market_brief.md").write_text(
        "Market regime transition indicators and volatility discussion.",
        encoding="utf-8",
    )

    records = ingest_paths(
        [*corpus.glob("*.md")], IngestionConfig(chunk_size=80, overlap=10)
    )
    return RetrievalIndex(records)


def test_known_item_retrieval(tmp_path: Path) -> None:
    index = _build_seed_index(tmp_path)
    results = index.retrieve("sanctions trade guidance", top_k=3)
    assert results
    assert results[0]["source_id"] == "canonical_policy"


def test_filtering_by_source_type_and_canonical(tmp_path: Path) -> None:
    index = _build_seed_index(tmp_path)
    results = index.retrieve("monitoring", filters={"canonical": True}, top_k=5)
    assert results
    for result in results:
        metadata = result["metadata"]
        assert isinstance(metadata, dict)
        assert metadata.get("canonical") is True


def test_result_shape_contains_required_contract_fields(tmp_path: Path) -> None:
    index = _build_seed_index(tmp_path)
    result: dict[str, Any] = index.retrieve("regime volatility", top_k=1)[0]
    assert set(result.keys()) == {
        "id",
        "source_id",
        "text",
        "score",
        "metadata",
        "provenance",
    }
    provenance = result["provenance"]
    assert isinstance(provenance, dict)
    assert provenance.get("source_id") == result["source_id"]
