from pathlib import Path

from forecasting_engine.config_loader import load_algorithm_defaults, validate_algorithm_defaults


def test_algorithm_defaults_satisfy_invariants() -> None:
    defaults = load_algorithm_defaults(Path("config"))
    validate_algorithm_defaults(defaults)
