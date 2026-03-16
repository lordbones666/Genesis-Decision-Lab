from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyBundle:
    logodds: str
    dedupe: str
    regime: str
    calibration: str
    market_path: str


DEFAULT_BUNDLE = PolicyBundle(
    logodds="logodds-v1.2",
    dedupe="dedupe-v1.1",
    regime="regime-v1.1",
    calibration="calibration-temperature-v1",
    market_path="market-path-v1.1",
)


def resolve_policy_bundle(question_id: str, domain: str) -> PolicyBundle:
    domain = domain.lower()
    if question_id == "K4" or domain == "energy":
        return DEFAULT_BUNDLE
    return DEFAULT_BUNDLE
