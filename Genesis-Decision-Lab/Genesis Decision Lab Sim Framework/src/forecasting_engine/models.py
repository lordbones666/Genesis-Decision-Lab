from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class TimeWindow:
    opens_at: datetime
    closes_at: datetime
    timezone: str


@dataclass(frozen=True)
class QuestionObject:
    question_id: str
    wording: str
    time_window: TimeWindow
    resolution_authority: str
    resolution_method: str
    binary_criteria: dict[str, str]
    event_definition: str = ""
    reference_class_key: str = ""
    invalidation_conditions: list[str] = field(default_factory=list)
    domain: str = "general"
    horizon: str = "default"
    version: str = "v1"


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    url: str
    retrieved_at: datetime
    publisher: str
    title: str = ""
    published_at: datetime | None = None
    extraction_notes: str = ""
    credibility_flags: list[str] = field(default_factory=list)
    quotes: list[str] = field(default_factory=list)
    content_hash: str = ""
    excerpt: str = ""
    archive_pointer: str = ""


@dataclass(frozen=True)
class StructuredEvidenceObject:
    event_id: str
    question_id: str
    timestamp: datetime
    category: str
    direction: int
    magnitude: str
    claim_type: str
    source_ids: list[str]
    source_tier: str
    resolver_authority: str = ""
    resolver_method: str = ""
    correction_of_event_id: str = ""
    cluster_id: str = ""
    cluster_key_fields: list[str] = field(default_factory=list)
    key_version: str = "v1"
    phi_version: str = "v1"
    revision_id: str = ""
    weight_raw: float = 0.0
    weight_effective: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ForecastSnapshot:
    question_id: str
    as_of: datetime
    probability: float
    logodds: float
    pre_logodds: float
    delta_logodds: float
    config_version: str
    evidence_ids: list[str]
    raw_delta_logodds: float = 0.0
    regime_adjustment: float = 0.0
    regime_entropy: float = 0.0
    ablation_label: str = "baseline"
    reversal_of_event_ids: list[str] = field(default_factory=list)
    model_version: str = "model-v1"
    cal_version: str = "cal-none"
    artifacts: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScoreRecord:
    question_id: str
    resolved_at: datetime
    outcome: int
    probability: float
    brier: float
    domain: str
    horizon: str
