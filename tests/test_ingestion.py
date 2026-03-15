from pathlib import Path

from retrieval.ingest import IngestionConfig, ingest_paths


def test_ingestion_emits_stable_chunk_ids(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    file_path = corpus / "policy.md"
    file_path.write_text("A" * 120 + "B" * 120, encoding="utf-8")

    config = IngestionConfig(chunk_size=100, overlap=20)
    first = ingest_paths([file_path], config)
    second = ingest_paths([file_path], config)

    assert [item.id for item in first] == [item.id for item in second]
    assert all(item.provenance["chunk_id"] == item.id for item in first)


def test_ingestion_includes_required_metadata_and_provenance(tmp_path: Path) -> None:
    source = tmp_path / "notes.md"
    source.write_text("retrieval substrate supports evidence lookup", encoding="utf-8")

    records = ingest_paths(
        [source], IngestionConfig(chunk_size=60, overlap=10, source_type="note")
    )

    assert records
    record = records[0]
    assert record.source_id == "notes"
    assert record.metadata["source_type"] == "note"
    assert "path" in record.metadata
    assert "timestamp" in record.metadata
    assert record.provenance["source_id"] == record.source_id
    assert "location" in record.provenance
