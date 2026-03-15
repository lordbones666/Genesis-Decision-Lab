from retrieval.contracts import RetrievalRequest, RetrievalResult, result_to_dict


def test_retrieval_request_defaults() -> None:
    request = RetrievalRequest(query="energy shocks")
    assert request.query == "energy shocks"
    assert request.top_k == 5
    assert request.filters is None


def test_retrieval_request_validation() -> None:
    try:
        RetrievalRequest(query="   ")
        assert False, "expected ValueError for empty query"
    except ValueError:
        pass

    try:
        RetrievalRequest(query="valid", top_k=0)
        assert False, "expected ValueError for non-positive top_k"
    except ValueError:
        pass


def test_result_to_dict_contains_required_fields() -> None:
    result = RetrievalResult(
        id="chunk-1",
        source_id="source-a",
        text="sample",
        score=1.5,
        metadata={"canonical": True},
        provenance={"chunk_id": "chunk-1"},
    )
    payload = result_to_dict(result)
    assert set(payload.keys()) == {
        "id",
        "source_id",
        "text",
        "score",
        "metadata",
        "provenance",
    }
