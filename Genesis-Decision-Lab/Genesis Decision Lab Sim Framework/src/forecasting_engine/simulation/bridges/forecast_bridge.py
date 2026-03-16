from __future__ import annotations

import hashlib
from datetime import timedelta

from forecasting_engine.models import StructuredEvidenceObject
from forecasting_engine.simulation.contracts import SimulationOutput


def simulation_to_evidence(
    simulation: SimulationOutput,
    question_id: str,
    category: str,
    source_tier: str = "tier2",
    run_id: str | None = None,
) -> StructuredEvidenceObject:
    event_key = f"{simulation.simulator}:{simulation.context.scenario_id}:{question_id}:{simulation.context.as_of.isoformat()}"
    event_id = hashlib.sha256(event_key.encode()).hexdigest()[:20]
    intensity = simulation.metrics.get("stress", 0.0) + simulation.metrics.get("crisis_share", 0.0)
    direction = 1 if intensity >= 0 else -1
    magnitude = "small" if abs(intensity) < 0.2 else "medium" if abs(intensity) < 0.5 else "large"
    return StructuredEvidenceObject(
        event_id=event_id,
        question_id=question_id,
        timestamp=simulation.context.as_of + timedelta(seconds=1),
        category=category,
        direction=direction,
        magnitude=magnitude,
        claim_type="simulation",
        source_ids=[f"sim::{simulation.simulator}"],
        source_tier=source_tier,
        metadata={
            "scenario_id": simulation.context.scenario_id,
            "config_version": simulation.context.config_version,
            "seed": simulation.context.seed,
            "metrics": simulation.metrics,
            "run_id": run_id,
        },
    )
