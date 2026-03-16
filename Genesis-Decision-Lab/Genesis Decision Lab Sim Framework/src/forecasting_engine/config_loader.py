from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from forecasting_engine.policies.logodds import validate_cfg as validate_logodds_cfg
from forecasting_engine.policies.regime import validate_cfg as validate_regime_cfg


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def load_config(config_dir: Path) -> dict[str, dict[str, Any]]:
    files = {
        "allowed_sources": "allowed_sources.json",
        "category_maps": "category_maps.json",
        "magnitude_tables": "magnitude_tables.json",
        "routing_maps": "routing_maps.json",
        "weights": "weight_tables.v1.json",
        "regime": "regime_params.v1.json",
        "change_control": "change_control.json",
        "base_rates": "base_rates.v1.json",
    }
    return {k: load_json(config_dir / v) for k, v in files.items()}


def load_algorithm_defaults(config_dir: Path) -> dict[str, dict[str, Any]]:
    files = {
        "logodds": "algorithms/logodds.default.v1.json",
        "dedupe": "algorithms/dedupe.default.v1.json",
        "regime": "algorithms/regime.default.v1.json",
        "calibration": "algorithms/calibration.default.v1.json",
    }
    return {k: load_json(config_dir / v) for k, v in files.items()}


def load_simulation_defaults(config_dir: Path) -> dict[str, dict[str, Any]]:
    files = {
        "framework": "simulation/framework.default.v1.json",
        "domains": "simulation/domains.default.v1.json",
    }
    return {k: load_json(config_dir / v) for k, v in files.items()}


def validate_algorithm_defaults(defaults: dict[str, dict[str, Any]]) -> None:
    logodds_errors = validate_logodds_cfg(defaults["logodds"])
    regime_errors = validate_regime_cfg(defaults["regime"])
    if logodds_errors or regime_errors:
        errors = logodds_errors + regime_errors
        raise ValueError(f"Algorithm defaults failed invariants: {errors}")


def validate_change_control(change: dict[str, Any]) -> None:
    required = [
        "component",
        "old_version",
        "new_version",
        "rationale",
        "expected_impact",
        "replay_diff",
    ]
    missing = [item for item in required if not change.get(item)]
    if missing:
        raise ValueError(f"Missing change control fields: {', '.join(missing)}")
    if change["old_version"] == change["new_version"]:
        raise ValueError("new_version must differ from old_version")


def load_scenario_defaults(config_dir: Path) -> dict[str, dict[str, Any]]:
    files = {
        "templates": "scenario/templates.default.v1.json",
    }
    return {k: load_json(config_dir / v) for k, v in files.items()}


def load_portfolio_defaults(config_dir: Path) -> dict[str, dict[str, Any]]:
    files = {
        "defaults": "portfolio/defaults.v1.json",
    }
    return {k: load_json(config_dir / v) for k, v in files.items()}


def load_automation_defaults(config_dir: Path) -> dict[str, dict[str, Any]]:
    files = {
        "triage": "automation/triage.default.v1.json",
    }
    return {k: load_json(config_dir / v) for k, v in files.items()}
