from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

HypothesisStatus = Literal["active", "weakened", "superseded", "unresolved"]


@dataclass(frozen=True)
class HypothesisRecord:
    hypothesis_id: str
    title: str
    description: str
    problem_family: str
    assumptions: list[str]
    supporting_evidence_ids: list[str] = field(default_factory=list)
    contradicting_evidence_ids: list[str] = field(default_factory=list)
    linked_models: list[str] = field(default_factory=list)
    current_weight: float = 0.5
    falsifiers: list[str] = field(default_factory=list)
    discriminating_signals: list[str] = field(default_factory=list)
    next_information_needed: list[str] = field(default_factory=list)
    status: HypothesisStatus = "unresolved"
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
