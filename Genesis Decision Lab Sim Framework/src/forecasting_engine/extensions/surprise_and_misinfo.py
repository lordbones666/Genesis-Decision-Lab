from __future__ import annotations

from dataclasses import dataclass

SURPRISE_SIGNALS = {
    "embassy_evacuation",
    "carrier_deployment",
    "national_mobilization",
    "nuclear_command_readiness",
}


@dataclass(frozen=True)
class SourceCredibilityAssessment:
    is_likely_misinformation: bool
    credibility_score: float


def is_surprise_signal(signal_type: str) -> bool:
    return signal_type in SURPRISE_SIGNALS


def misinformation_score(
    source_tier: str,
    bot_amplified: bool,
    ai_generated_media_flag: bool,
    recycled_footage_flag: bool,
) -> SourceCredibilityAssessment:
    base = {"tier_1": 0.9, "tier_2": 0.7, "tier_3": 0.45}.get(source_tier, 0.3)
    penalties = 0.0
    if bot_amplified:
        penalties += 0.25
    if ai_generated_media_flag:
        penalties += 0.35
    if recycled_footage_flag:
        penalties += 0.25
    score = max(min(base - penalties, 1.0), 0.0)
    return SourceCredibilityAssessment(
        is_likely_misinformation=score < 0.3, credibility_score=score
    )
