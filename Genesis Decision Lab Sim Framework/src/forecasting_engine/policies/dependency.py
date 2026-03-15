from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DependencyTracker:
    channels: dict[str, set[str]] = field(default_factory=dict)

    def declare_inputs_used(self, channel: str, feature_ids: set[str]) -> None:
        self.channels.setdefault(channel, set()).update(feature_ids)

    def overlap(self, channel_a: str, channel_b: str) -> set[str]:
        return self.channels.get(channel_a, set()) & self.channels.get(channel_b, set())


def dependency_safe_blend(
    primary: float,
    secondary: float,
    overlap_features: set[str],
    allow_overlap: bool,
    overlap_penalty: float,
) -> tuple[float, dict[str, float | bool | int]]:
    if overlap_features and not allow_overlap:
        return primary, {
            "dependency_blocked": True,
            "overlap_count": len(overlap_features),
            "blend_weight": 0.0,
        }
    weight = max(min(1.0 - overlap_penalty * len(overlap_features), 1.0), 0.0)
    blended = (1.0 - weight) * primary + weight * secondary
    return blended, {
        "dependency_blocked": False,
        "overlap_count": len(overlap_features),
        "blend_weight": weight,
    }
