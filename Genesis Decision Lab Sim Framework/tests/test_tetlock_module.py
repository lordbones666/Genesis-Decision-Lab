from datetime import UTC, datetime, timedelta

from forecasting_engine.extensions.tetlock_module import (
    SentimentDocument,
    causal_graph_propagation,
    decomposition_and_chain,
    decomposition_noisy_or,
    default_dashboard,
    domain_map,
    event_tree_simulation,
    evidence_status,
    good_question_check,
    logodds_update,
    question_factory,
    select_base_rate,
    sentiment_layer,
    sentiment_to_delta,
)


def test_question_factory_and_gate() -> None:
    now = datetime.now(UTC)
    qo = question_factory(
        "Q1",
        "Will X happen?",
        "binary",
        "official resolver says yes",
        ["official"],
        now,
        now + timedelta(days=7),
        "ref_key",
    )
    gate = good_question_check(qo)
    assert gate.ok


def test_base_rate_decomposition_and_update() -> None:
    base = {
        "default": {"prior_p": 0.5, "prior_confidence": "low", "reference_examples": []},
        "key": {"prior_p": 0.4, "prior_confidence": "med", "reference_examples": ["a"]},
    }
    selected = select_base_rate("key", base)
    assert selected.prior_p == 0.4
    assert decomposition_and_chain([0.5, 0.5]) == 0.25
    noisy = decomposition_noisy_or([(0.5, 0.5), (0.5, 0.5)])
    assert 0.0 < noisy < 1.0
    post, delta = logodds_update(0.5, [0.1, 0.2], cap=1.0)
    assert 0.0 < post < 1.0
    assert delta == 0.30000000000000004 or abs(delta - 0.3) < 1e-12


def test_causal_and_simulation() -> None:
    updated = causal_graph_propagation({"A": 0.2, "B": 0.2}, [("A", "B", 0.5)], "A", 0.2)
    assert updated["B"] > 0.2
    sim = event_tree_simulation(0.8, 0.5, 0.5, runs=500, seed=7)
    assert 0.0 <= sim <= 1.0


def test_sentiment_layer_and_mapping() -> None:
    docs = [
        SentimentDocument(0.8, 0.7, 0.8, "tier_1", 1.0, "a"),
        SentimentDocument(0.6, 0.6, 0.7, "tier_2", 3.0, "b"),
    ]
    sentiment = sentiment_layer(docs, prev_volume=1)
    delta = sentiment_to_delta(sentiment)
    assert sentiment.volume == 2
    assert -1.0 <= sentiment.sps <= 1.0
    assert -0.2 <= delta <= 0.2


def test_domain_map_dashboard_and_status() -> None:
    dmap = domain_map()
    assert "markets" in dmap
    panels = default_dashboard()
    assert len(panels) >= 2
    status = evidence_status([])
    assert status == "Unverified"
