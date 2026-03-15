from __future__ import annotations

from dataclasses import dataclass

from forecasting_engine.automation.diff_detector import detect_changed_fields

TRIAGE_INFORMATIONAL = "informational"
TRIAGE_EVIDENCE_ONLY = "evidence_only"
TRIAGE_SCENARIO_AFFECTING = "scenario_affecting"
TRIAGE_RERUN_REQUIRED = "rerun_required"
TRIAGE_OPERATOR_REVIEW_REQUIRED = "operator_review_required"


@dataclass(frozen=True)
class TriageDecision:
    category: str
    reason: str
    changed_fields: tuple[str, ...]


def classify_update(previous: dict[str, object], current: dict[str, object]) -> TriageDecision:
    changed = detect_changed_fields(previous, current)
    ordered = tuple(sorted(changed))
    if not changed:
        return TriageDecision(TRIAGE_INFORMATIONAL, "No state diff detected.", ordered)
    if "manual_override" in changed:
        return TriageDecision(
            TRIAGE_OPERATOR_REVIEW_REQUIRED,
            "Manual override changed; operator verification is required.",
            ordered,
        )
    if changed <= {"evidence_ids", "evidence_snapshot_hash"}:
        return TriageDecision(
            TRIAGE_EVIDENCE_ONLY,
            "Only evidence linkage changed; scenario compilation unchanged.",
            ordered,
        )
    if changed & {"scenario_id", "trigger_set", "state_assumptions", "regime_assumptions"}:
        return TriageDecision(
            TRIAGE_SCENARIO_AFFECTING,
            "Scenario-defining fields changed.",
            ordered,
        )
    return TriageDecision(
        TRIAGE_RERUN_REQUIRED,
        "Run-relevant state changed outside evidence-only scope.",
        ordered,
    )
