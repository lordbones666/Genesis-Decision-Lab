from pathlib import Path

import pytest

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
    assert [item.source_id for item in first] == [item.source_id for item in second]
    assert all(item.provenance["chunk_id"] == item.id for item in first)


def test_ingestion_handles_empty_corpus() -> None:
    assert ingest_paths([]) == []


def test_ingestion_rejects_missing_paths(tmp_path: Path) -> None:
    missing = tmp_path / "missing.md"
    with pytest.raises(FileNotFoundError):
        ingest_paths([missing])


def test_ingestion_rejects_directories(tmp_path: Path) -> None:
    with pytest.raises(IsADirectoryError):
        ingest_paths([tmp_path])


def test_single_file_source_id_is_stable_with_same_filename(tmp_path: Path) -> None:
    config = IngestionConfig(chunk_size=80, overlap=10)

    base_one = tmp_path / "first"
    base_two = tmp_path / "second"
    base_one.mkdir(parents=True, exist_ok=True)
    base_two.mkdir(parents=True, exist_ok=True)

    first_path = base_one / "policy.md"
    second_path = base_two / "policy.md"
    first_path.write_text("same content", encoding="utf-8")
    second_path.write_text("same content", encoding="utf-8")

    first_records = ingest_paths([first_path], config)
    second_records = ingest_paths([second_path], config)

    assert first_records
    assert second_records
    assert first_records[0].source_id == second_records[0].source_id


def test_ingestion_source_ids_do_not_collide_for_duplicate_stems(
    tmp_path: Path,
) -> None:
    a_dir = tmp_path / "a"
    b_dir = tmp_path / "b"
    a_dir.mkdir()
    b_dir.mkdir()
    a_file = a_dir / "policy.md"
    b_file = b_dir / "policy.md"
    a_file.write_text("sanctions update", encoding="utf-8")
    b_file.write_text("trade update", encoding="utf-8")

    records = ingest_paths([a_file, b_file], IngestionConfig(chunk_size=80, overlap=10))
    source_ids = {record.source_id for record in records}

    assert len(source_ids) == 2


def test_ingestion_includes_required_metadata_and_provenance(tmp_path: Path) -> None:
    source = tmp_path / "notes.md"
    source.write_text("retrieval substrate supports evidence lookup", encoding="utf-8")

    records = ingest_paths(
        [source], IngestionConfig(chunk_size=60, overlap=10, source_type="note")
    )

    assert records
    record = records[0]
    assert record.source_id.startswith("notes-")
    assert record.metadata["source_type"] == "note"
    assert "path" in record.metadata
    assert "timestamp" in record.metadata
    assert record.provenance["source_id"] == record.source_id
    assert "location" in record.provenance
