from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TacticalSignal:
    signal_type: str
    observed_at: datetime
    entity: str
    intensity: float
    source: str


def signal_weight(signal: TacticalSignal) -> float:
    base = {
        "tanker_launch_wave": 0.08,
        "airspace_closure": 0.06,
        "carrier_movement": 0.07,
        "embassy_evacuation": 0.10,
    }.get(signal.signal_type, 0.03)
    return base * max(signal.intensity, 0.0)


def signal_to_evidence_note(signal: TacticalSignal) -> str:
    return (
        f"OSINT signal={signal.signal_type} entity={signal.entity} "
        f"intensity={signal.intensity:.2f} source={signal.source}"
    )
