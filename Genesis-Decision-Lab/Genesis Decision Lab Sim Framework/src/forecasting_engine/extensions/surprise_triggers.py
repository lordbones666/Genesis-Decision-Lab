from __future__ import annotations

SURPRISE_RULES = {
    "embassy_evacuation": 0.25,
    "emergency_central_bank_meeting": 0.20,
    "exchange_withdrawals_halted": 0.30,
}


def trigger_delta(trigger_name: str) -> float:
    return SURPRISE_RULES.get(trigger_name, 0.0)
