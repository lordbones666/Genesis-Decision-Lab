from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from forecasting_engine.ledger import JsonlLedger
from forecasting_engine.simulation.contracts import SimulationRunRecord


class SimulationRunLedger(JsonlLedger):
    def __init__(self, path: Path) -> None:
        super().__init__(path)

    def append_run(self, run_record: SimulationRunRecord) -> None:
        self.append(asdict(run_record))
