from forecasting_engine.pipeline import monte_carlo


def test_monte_carlo_determinism() -> None:
    p1 = monte_carlo(80.0, 90.0, 0.08, 0.3, 60, 500, seed=42)
    p2 = monte_carlo(80.0, 90.0, 0.08, 0.3, 60, 500, seed=42)
    assert p1 == p2
    assert 0.0 <= p1 <= 1.0
