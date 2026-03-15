from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any


@dataclass(frozen=True)
class QuestionObjectUniversal:
    question_id: str
    title: str
    type: str
    resolution_criteria: str
    resolver_sources: list[str]
    start_time: datetime
    end_time: datetime
    reference_class_key: str
    notes: str = ""


@dataclass(frozen=True)
class GoodQuestionGateResult:
    ok: bool
    issues: list[str]


@dataclass(frozen=True)
class BaseRateResult:
    prior_p: float
    prior_confidence: str
    reference_examples: list[str]


@dataclass(frozen=True)
class EvidenceObject:
    evidence_id: str
    timestamp: datetime
    claim: str
    supports_question_ids: list[str]
    direction: int
    strength: str
    source_tier: str
    reliability_notes: str
    extract: str
    links: list[str]


@dataclass(frozen=True)
class ForecastSnapshotUniversal:
    snapshot_id: str
    question_id: str
    as_of: datetime
    p: float
    prior_p: float
    delta_logodds_total: float
    evidence_ids: list[str]
    reasoning_summary: str
    confidence: str
    next_signals_to_watch: list[str]


@dataclass(frozen=True)
class SentimentDocument:
    polarity: float
    arousal: float
    certainty: float
    source_tier: str
    hours_ago: float
    text: str


@dataclass(frozen=True)
class SentimentResult:
    sps: float
    nhi: float
    volume: int
    velocity: float
    agreement: float


@dataclass(frozen=True)
class DashboardPanel:
    panel_name: str
    questions: list[QuestionObjectUniversal]
    latent_drivers: list[str]


@dataclass
class TetlockState:
    question_objects: dict[str, QuestionObjectUniversal] = field(default_factory=dict)
    evidence_ledger: list[EvidenceObject] = field(default_factory=list)
    forecast_ledger: list[ForecastSnapshotUniversal] = field(default_factory=list)


def question_factory(
    question_id: str,
    title: str,
    q_type: str,
    resolution_criteria: str,
    resolver_sources: list[str],
    start_time: datetime,
    end_time: datetime,
    reference_class_key: str,
    notes: str = "",
) -> QuestionObjectUniversal:
    return QuestionObjectUniversal(
        question_id=question_id,
        title=title,
        type=q_type,
        resolution_criteria=resolution_criteria,
        resolver_sources=resolver_sources,
        start_time=start_time,
        end_time=end_time,
        reference_class_key=reference_class_key,
        notes=notes,
    )


def good_question_check(question: QuestionObjectUniversal) -> GoodQuestionGateResult:
    issues: list[str] = []
    if not question.resolution_criteria:
        issues.append("missing_resolution_criteria")
    if question.type not in {"binary", "numeric_threshold", "numeric_range"}:
        issues.append("invalid_type")
    if not question.resolver_sources:
        issues.append("missing_resolver_sources")
    if question.end_time <= question.start_time:
        issues.append("invalid_time_window")
    if not question.reference_class_key:
        issues.append("missing_reference_class_key")
    return GoodQuestionGateResult(ok=not issues, issues=issues)


def select_base_rate(
    reference_class_key: str, base_rate_table: dict[str, dict[str, Any]]
) -> BaseRateResult:
    row = base_rate_table.get(reference_class_key, base_rate_table["default"])
    return BaseRateResult(
        prior_p=float(row["prior_p"]),
        prior_confidence=str(row.get("prior_confidence", "low")),
        reference_examples=list(row.get("reference_examples", [])),
    )


def decomposition_and_chain(probabilities: list[float]) -> float:
    out = 1.0
    for value in probabilities:
        out *= min(max(value, 0.0), 1.0)
    return out


def decomposition_noisy_or(weighted_causes: list[tuple[float, float]]) -> float:
    product = 1.0
    for weight, prob in weighted_causes:
        product *= 1 - min(max(weight * prob, 0.0), 1.0)
    return 1.0 - product


def evidence_status(evidence: list[EvidenceObject]) -> str:
    tiers = {item.source_tier for item in evidence}
    if "tier_1" in tiers:
        return "Verified"
    if len(tiers) > 1 or "tier_2" in tiers:
        return "Contested"
    return "Unverified"


def logodds_update(prior_p: float, deltas: list[float], cap: float = 1.0) -> tuple[float, float]:
    prior = min(max(prior_p, 1e-6), 1 - 1e-6)
    prior_l = math.log(prior / (1 - prior))
    total = sum(deltas)
    clipped = max(min(total, cap), -cap)
    post_l = prior_l + clipped
    post = 1 / (1 + math.exp(-post_l))
    return post, clipped


def causal_graph_propagation(
    base: dict[str, float], edges: list[tuple[str, str, float]], source: str, delta: float
) -> dict[str, float]:
    out = dict(base)
    out[source] = min(max(out.get(source, 0.5) + delta, 0.0), 1.0)
    for src, dst, weight in edges:
        if src == source:
            out[dst] = min(max(out.get(dst, 0.5) + delta * weight, 0.0), 1.0)
    return out


def event_tree_simulation(
    release_prob: float, novelty_prob: float, notable_prob: float, runs: int, seed: int
) -> float:
    import random

    rng = random.Random(seed)
    success = 0
    for _ in range(runs):
        release = rng.random() < release_prob
        novelty = rng.random() < novelty_prob
        notable = rng.random() < notable_prob
        if release and novelty and notable:
            success += 1
    return success / runs


def _tier_weight(source_tier: str) -> float:
    return {"tier_1": 1.0, "tier_2": 0.7, "tier_3": 0.35}.get(source_tier, 0.25)


def _freshness(hours_ago: float, tau: float = 36.0) -> float:
    return math.exp(-max(hours_ago, 0.0) / tau)


def sentiment_layer(documents: list[SentimentDocument], prev_volume: int) -> SentimentResult:
    if not documents:
        return SentimentResult(0.0, 0.0, 0, 0.0, 1.0)

    per_doc: list[float] = []
    polarities: list[float] = []
    arousals: list[float] = []
    for doc in documents:
        value = (
            doc.polarity
            * (0.6 + 0.4 * doc.arousal)
            * (0.5 + 0.5 * doc.certainty)
            * _tier_weight(doc.source_tier)
            * _freshness(doc.hours_ago)
        )
        per_doc.append(min(max(value, -1.0), 1.0))
        polarities.append(doc.polarity)
        arousals.append(doc.arousal)

    per_doc.sort()
    trim = max(int(0.1 * len(per_doc)), 0)
    trimmed = per_doc[trim : len(per_doc) - trim] if len(per_doc) - 2 * trim > 0 else per_doc
    sps = min(max(sum(trimmed) / len(trimmed), -1.0), 1.0)

    volume = len(documents)
    velocity = (volume - prev_volume) / max(prev_volume, 1)
    agreement = 1.0 - min(
        sum(abs(p - sum(polarities) / len(polarities)) for p in polarities) / len(polarities), 1.0
    )
    a_mean = sum(arousals) / len(arousals)
    z = 1.2 * math.log(max(volume, 1)) + 1.0 * velocity + 0.8 * a_mean - 0.6 * agreement
    nhi = 100 * (1 / (1 + math.exp(-z)))
    return SentimentResult(sps=sps, nhi=nhi, volume=volume, velocity=velocity, agreement=agreement)


def sentiment_to_delta(sentiment: SentimentResult) -> float:
    abs_sps = abs(sentiment.sps)
    if abs_sps < 0.15:
        return 0.0
    if abs_sps < 0.35:
        magnitude = 0.05
    elif abs_sps < 0.55:
        magnitude = 0.12
    elif sentiment.nhi > 70:
        magnitude = 0.20
    else:
        magnitude = 0.12
    return magnitude if sentiment.sps > 0 else -magnitude


def domain_map() -> dict[str, dict[str, list[str]]]:
    return {
        "markets": {
            "resolvers": ["exchange_data", "index_provider", "sec_filings", "cboe"],
            "question_types": ["threshold", "event", "regime"],
        },
        "tech": {
            "resolvers": ["official_announcements", "changelogs", "regulatory_filings"],
            "question_types": ["milestone", "adoption_threshold"],
        },
        "geopolitics": {
            "resolvers": ["official_statements", "election_commissions", "un_records"],
            "question_types": ["occurrence", "cascade", "policy"],
        },
        "investigations": {
            "resolvers": ["court_dockets", "agency_releases", "foia_logs"],
            "question_types": ["discovery", "process"],
        },
        "science": {
            "resolvers": ["peer_review", "trial_registries", "fda_ema"],
            "question_types": ["milestone", "threshold"],
        },
        "conflicts": {
            "resolvers": ["acled_ucdp", "official_reports", "credible_investigations"],
            "question_types": ["occurrence", "cascade", "threshold"],
        },
        "society": {
            "resolvers": ["official_stats", "legislative_records", "reputable_surveys"],
            "question_types": ["threshold", "policy"],
        },
    }


def default_dashboard() -> list[DashboardPanel]:
    now = datetime.now(UTC)
    return [
        DashboardPanel(
            "Markets Panel",
            [
                question_factory(
                    "MKT1",
                    "Will VIX exceed 40 by horizon?",
                    "numeric_threshold",
                    "VIX > 40",
                    ["cboe"],
                    now,
                    now + timedelta(days=30),
                    "markets_vix_40",
                )
            ],
            ["liquidity", "volatility"],
        ),
        DashboardPanel(
            "Geo/Conflict Panel",
            [
                question_factory(
                    "GEO1",
                    "Will chokepoint close by horizon?",
                    "binary",
                    "closure declared by authority",
                    ["official_statements"],
                    now,
                    now + timedelta(days=30),
                    "conflict_chokepoint",
                )
            ],
            ["escalation_regime", "institutional_pressure"],
        ),
    ]


def state_to_dict(state: TetlockState) -> dict[str, Any]:
    return {
        "question_objects": {k: asdict(v) for k, v in state.question_objects.items()},
        "evidence_ledger": [asdict(item) for item in state.evidence_ledger],
        "forecast_ledger": [asdict(item) for item in state.forecast_ledger],
    }
