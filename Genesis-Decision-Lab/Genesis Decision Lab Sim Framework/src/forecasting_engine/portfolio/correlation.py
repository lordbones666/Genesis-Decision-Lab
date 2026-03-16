from __future__ import annotations


def compute_scenario_overlap(
    forecast_to_scenarios: dict[str, set[str]],
) -> dict[str, float]:
    overlap: dict[str, float] = {}
    ordered_ids = sorted(forecast_to_scenarios)
    for i, left in enumerate(ordered_ids):
        for right in ordered_ids[i + 1 :]:
            left_set = forecast_to_scenarios[left]
            right_set = forecast_to_scenarios[right]
            union = left_set | right_set
            jaccard = (len(left_set & right_set) / len(union)) if union else 0.0
            overlap[f"{left}|{right}"] = round(jaccard, 6)
    return overlap
