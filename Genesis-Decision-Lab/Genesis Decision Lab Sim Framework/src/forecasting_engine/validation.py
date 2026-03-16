from __future__ import annotations

from datetime import datetime
from typing import Any

from forecasting_engine.models import (
    QuestionObject,
    SourceRecord,
    StructuredEvidenceObject,
    TimeWindow,
)


class ValidationError(ValueError):
    """Validation failure."""


ALLOWED_SOURCE_TIERS = {"tier_1", "tier_2", "tier_3"}


def _require(data: dict[str, Any], keys: list[str]) -> None:
    for key in keys:
        if key not in data or data[key] in (None, ""):
            msg = f"Missing required field: {key}"
            raise ValidationError(msg)


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_question_object(payload: dict[str, Any]) -> QuestionObject:
    _require(
        payload,
        [
            "question_id",
            "wording",
            "time_window",
            "resolution_authority",
            "resolution_method",
            "binary_criteria",
            "event_definition",
            "reference_class_key",
            "version",
        ],
    )
    tw = payload["time_window"]
    _require(tw, ["opens_at", "closes_at", "timezone"])
    opens_at = parse_datetime(tw["opens_at"])
    closes_at = parse_datetime(tw["closes_at"])
    if closes_at <= opens_at:
        raise ValidationError("time_window closes_at must be greater than opens_at")
    criteria = payload["binary_criteria"]
    _require(criteria, ["yes_definition", "no_definition"])

    return QuestionObject(
        question_id=payload["question_id"],
        wording=payload["wording"],
        time_window=TimeWindow(opens_at=opens_at, closes_at=closes_at, timezone=tw["timezone"]),
        resolution_authority=payload["resolution_authority"],
        resolution_method=payload["resolution_method"],
        binary_criteria=criteria,
        event_definition=payload.get("event_definition", ""),
        reference_class_key=payload.get("reference_class_key", ""),
        invalidation_conditions=payload.get("invalidation_conditions", []),
        domain=payload.get("domain", "general"),
        horizon=payload.get("horizon", "default"),
        version=payload["version"],
    )


def question_gate(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    issues: list[str] = []
    for key in [
        "resolution_authority",
        "resolution_method",
        "time_window",
        "binary_criteria",
        "event_definition",
        "reference_class_key",
    ]:
        if not payload.get(key):
            issues.append(f"missing_{key}")

    time_window = payload.get("time_window", {})
    if time_window and (not time_window.get("opens_at") or not time_window.get("closes_at")):
        issues.append("ambiguous_time_window")
    elif time_window:
        try:
            opens_at = parse_datetime(str(time_window["opens_at"]))
            closes_at = parse_datetime(str(time_window["closes_at"]))
            if closes_at <= opens_at:
                issues.append("invalid_time_window_order")
        except (KeyError, TypeError, ValueError):
            issues.append("ambiguous_time_window")

    criteria = payload.get("binary_criteria", {})
    if criteria and (not criteria.get("yes_definition") or not criteria.get("no_definition")):
        issues.append("incomplete_binary_criteria")
    if not payload.get("wording"):
        issues.append("missing_wording")
    return len(issues) == 0, issues


def validate_source_record(payload: dict[str, Any]) -> SourceRecord:
    _require(payload, ["source_id", "url", "retrieved_at", "publisher"])
    return SourceRecord(
        source_id=payload["source_id"],
        url=payload["url"],
        retrieved_at=parse_datetime(payload["retrieved_at"]),
        publisher=payload["publisher"],
        title=payload.get("title", ""),
        published_at=(
            parse_datetime(payload["published_at"]) if payload.get("published_at") else None
        ),
        extraction_notes=payload.get("extraction_notes", ""),
        credibility_flags=payload.get("credibility_flags", []),
        quotes=payload.get("quotes", []),
        content_hash=payload.get("content_hash", ""),
        excerpt=payload.get("excerpt", ""),
        archive_pointer=payload.get("archive_pointer", ""),
    )


def validate_seo(payload: dict[str, Any]) -> StructuredEvidenceObject:
    _require(
        payload,
        [
            "event_id",
            "question_id",
            "timestamp",
            "category",
            "direction",
            "magnitude",
            "claim_type",
            "source_ids",
            "source_tier",
        ],
    )
    direction = int(payload["direction"])
    if direction not in (-1, 0, 1):
        raise ValidationError("direction must be -1, 0, or 1")
    if payload["magnitude"] not in {"small", "medium", "large"}:
        raise ValidationError("magnitude must be small|medium|large")
    source_tier = str(payload["source_tier"])
    if source_tier not in ALLOWED_SOURCE_TIERS:
        raise ValidationError("source_tier must be tier_1|tier_2|tier_3")
    if not payload["source_ids"]:
        raise ValidationError("source_ids must include at least one source")

    return StructuredEvidenceObject(
        event_id=payload["event_id"],
        question_id=payload["question_id"],
        timestamp=parse_datetime(payload["timestamp"]),
        category=payload["category"],
        direction=direction,
        magnitude=payload["magnitude"],
        claim_type=payload["claim_type"],
        source_ids=list(payload["source_ids"]),
        source_tier=source_tier,
        resolver_authority=payload.get("resolver_authority", ""),
        resolver_method=payload.get("resolver_method", ""),
        correction_of_event_id=payload.get("correction_of_event_id", ""),
        cluster_id=payload.get("cluster_id", ""),
        cluster_key_fields=list(payload.get("cluster_key_fields", [])),
        key_version=payload.get("key_version", "v1"),
        phi_version=payload.get("phi_version", "v1"),
        revision_id=payload.get("revision_id", ""),
        weight_raw=float(payload.get("weight_raw", 0.0)),
        weight_effective=float(payload.get("weight_effective", 0.0)),
        metadata=payload.get("metadata", {}),
    )
