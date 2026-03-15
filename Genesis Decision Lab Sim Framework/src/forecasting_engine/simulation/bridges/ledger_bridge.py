from __future__ import annotations

import hashlib
import json

from forecasting_engine.ledger import JsonlLedger
from forecasting_engine.simulation.contracts import SimulationOutput, SimulationRunRecord


class SimulationLedger(JsonlLedger):
    def append_simulation(self, output: SimulationOutput) -> None:
        payload = {
            "simulator": output.simulator,
            "scenario_id": output.context.scenario_id,
            "as_of": output.context.as_of,
            "horizon_steps": output.context.horizon_steps,
            "seed": output.context.seed,
            "config_version": output.context.config_version,
            "state": output.state,
            "metrics": output.metrics,
            "assumptions": output.assumptions,
            "artifacts": output.artifacts,
        }
        self.append(payload)


def _stable_hash(payload: dict[str, object]) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()


def build_run_record(
    *,
    output: SimulationOutput,
    simulator_version: str,
    evidence_snapshot: dict[str, object],
    regime_snapshot: dict[str, float],
    failed: bool = False,
    failure_reason: str | None = None,
) -> SimulationRunRecord:
    evidence_snapshot_hash = _stable_hash(evidence_snapshot)
    run_key = {
        "simulator": output.simulator,
        "scenario_id": output.context.scenario_id,
        "as_of": output.context.as_of.isoformat(),
        "seed": output.context.seed,
        "config_version": output.context.config_version,
        "simulator_version": simulator_version,
        "evidence_snapshot_hash": evidence_snapshot_hash,
    }
    run_id = _stable_hash(run_key)[:20]
    return SimulationRunRecord(
        run_id=run_id,
        simulator=output.simulator,
        simulator_version=simulator_version,
        scenario_id=output.context.scenario_id,
        as_of=output.context.as_of,
        seed=output.context.seed,
        config_version=output.context.config_version,
        evidence_snapshot_hash=evidence_snapshot_hash,
        regime_snapshot=dict(sorted(regime_snapshot.items())),
        output_summary={
            "generated_at": output.context.as_of.isoformat(),
            "metrics": output.metrics,
            "state": output.state,
        },
        failed=failed,
        failure_reason=failure_reason,
    )
