from forecasting_engine.validation import (
    ValidationError,
    question_gate,
    validate_question_object,
    validate_seo,
    validate_source_record,
)


def test_question_validation_rejects_missing_resolution() -> None:
    payload = {
        "question_id": "C1",
        "wording": "Will X happen?",
        "time_window": {
            "opens_at": "2026-01-01T00:00:00Z",
            "closes_at": "2026-02-01T00:00:00Z",
            "timezone": "UTC",
        },
        "binary_criteria": {"yes_definition": "yes", "no_definition": "no"},
        "version": "v1",
    }

    try:
        validate_question_object(payload)
    except ValidationError:
        pass
    else:
        raise AssertionError("Expected ValidationError")


def test_question_gate_detects_missing_fields() -> None:
    ok, issues = question_gate({"wording": "test"})
    assert not ok
    assert "missing_resolution_authority" in issues


def test_question_gate_rejects_bad_time_order() -> None:
    payload = {
        "wording": "test",
        "resolution_authority": "EIA",
        "resolution_method": "WPSR",
        "time_window": {
            "opens_at": "2026-01-02T00:00:00Z",
            "closes_at": "2026-01-01T00:00:00Z",
            "timezone": "UTC",
        },
        "binary_criteria": {"yes_definition": "yes", "no_definition": "no"},
    }
    ok, issues = question_gate(payload)
    assert not ok
    assert "invalid_time_window_order" in issues


def test_source_record_requires_retrieval_fields() -> None:
    sr = validate_source_record(
        {
            "source_id": "sr1",
            "url": "https://example.com",
            "publisher": "example",
            "retrieved_at": "2026-01-01T00:00:00Z",
            "title": "Headline",
            "content_hash": "abc",
            "excerpt": "snippet",
        }
    )
    assert sr.url == "https://example.com"


def test_validate_seo_rejects_invalid_source_tier() -> None:
    payload = {
        "event_id": "e1",
        "question_id": "C1",
        "timestamp": "2026-01-01T00:00:00Z",
        "category": "security",
        "direction": 1,
        "magnitude": "small",
        "claim_type": "event",
        "source_ids": ["s1"],
        "source_tier": "tier_9",
    }
    try:
        validate_seo(payload)
    except ValidationError:
        pass
    else:
        raise AssertionError("Expected ValidationError")
