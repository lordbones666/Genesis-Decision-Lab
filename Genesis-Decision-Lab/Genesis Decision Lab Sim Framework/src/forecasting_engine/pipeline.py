from __future__ import annotations

import hashlib
import math
import random
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse

from forecasting_engine.models import ForecastSnapshot, SourceRecord, StructuredEvidenceObject
from forecasting_engine.policies.dedupe import (
    aggregate_cluster,
    deterministic_cluster_id,
    similarity_fingerprint,
)
from forecasting_engine.policies.dependency import DependencyTracker, dependency_safe_blend
from forecasting_engine.policies.logodds import update_logodds_policy
from forecasting_engine.policies.regime import apply_regime_offset
from forecasting_engine.validation import validate_seo, validate_source_record


def web_search_fetch(query: str, search_results: list[dict[str, str]]) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    now = datetime.now(timezone.utc)
    for idx, result in enumerate(search_results):
        raw_text = f"{result.get('title', '')}\n{result.get('snippet', '')}".strip()
        source_id = hashlib.sha256(f"{query}:{result.get('url', '')}:{idx}".encode()).hexdigest()[
            :16
        ]
        payload: dict[str, Any] = {
            "source_id": source_id,
            "url": result["url"],
            "publisher": result.get("publisher", urlparse(result["url"]).netloc),
            "title": result.get("title", ""),
            "retrieved_at": now.isoformat(),
            "published_at": result.get("published_at"),
            "extraction_notes": result.get("snippet", ""),
            "credibility_flags": [],
            "quotes": [],
            "content_hash": hashlib.sha256(raw_text.encode()).hexdigest(),
            "excerpt": raw_text[:500],
            "archive_pointer": result.get("archive_pointer", ""),
        }
        records.append(validate_source_record(payload))
    return records


def sr_to_seo(
    question_id: str,
    source_records: list[SourceRecord],
    category: str,
    source_tier: str,
    direction: int,
    magnitude: str,
    claim_type: str,
    correction_of_event_id: str = "",
    phi_version: str = "v1",
) -> list[StructuredEvidenceObject]:
    seos: list[StructuredEvidenceObject] = []
    for source in source_records:
        key_fields = [
            question_id,
            category,
            claim_type,
            (source.published_at or source.retrieved_at).date().isoformat(),
        ]
        cluster_id = deterministic_cluster_id(key_fields)
        fingerprint = similarity_fingerprint(
            f"{source.title}:{source.extraction_notes}:{question_id}:{category}:{claim_type}"
        )
        claim = (
            f"{source.title}:{source.extraction_notes}:{question_id}:{category}:{direction}:"
            f"{magnitude}:{claim_type}:{correction_of_event_id}"
        )
        event_id = hashlib.sha256(claim.encode()).hexdigest()[:20]
        payload: dict[str, Any] = {
            "event_id": event_id,
            "question_id": question_id,
            "timestamp": (source.published_at or source.retrieved_at).isoformat(),
            "category": category,
            "direction": direction,
            "magnitude": magnitude,
            "claim_type": claim_type,
            "source_ids": [source.source_id],
            "source_tier": source_tier,
            "correction_of_event_id": correction_of_event_id,
            "cluster_id": cluster_id,
            "cluster_key_fields": key_fields,
            "key_version": "v1",
            "phi_version": phi_version,
            "revision_id": source.content_hash,
            "metadata": {
                "url": source.url,
                "publisher": source.publisher,
                "content_hash": source.content_hash,
                "archive_pointer": source.archive_pointer,
                **fingerprint,
            },
        }
        seos.append(validate_seo(payload))
    return seos


def dedupe_cluster(
    seos: list[StructuredEvidenceObject],
) -> tuple[list[StructuredEvidenceObject], dict[str, str]]:
    clustered: dict[str, StructuredEvidenceObject] = {}
    provenance: dict[str, str] = {}
    for seo in sorted(seos, key=lambda e: e.timestamp):
        key = seo.cluster_id or (
            f"{seo.question_id}|{seo.category}|{seo.direction}|{seo.magnitude}|"
            f"{seo.claim_type}|{seo.correction_of_event_id}"
        )
        existing = clustered.get(key)
        if existing is None:
            clustered[key] = seo
            provenance[seo.event_id] = seo.event_id
            continue
        merged_sources = sorted(set(existing.source_ids + seo.source_ids))
        merged = StructuredEvidenceObject(
            event_id=existing.event_id,
            question_id=existing.question_id,
            timestamp=min(existing.timestamp, seo.timestamp),
            category=existing.category,
            direction=existing.direction,
            magnitude=existing.magnitude,
            claim_type=existing.claim_type,
            source_ids=merged_sources,
            source_tier=existing.source_tier,
            resolver_authority=existing.resolver_authority,
            resolver_method=existing.resolver_method,
            correction_of_event_id=existing.correction_of_event_id,
            cluster_id=existing.cluster_id,
            cluster_key_fields=existing.cluster_key_fields,
            key_version=existing.key_version,
            phi_version=existing.phi_version,
            revision_id=existing.revision_id,
            weight_raw=existing.weight_raw,
            weight_effective=existing.weight_effective,
            metadata=existing.metadata,
        )
        clustered[key] = merged
        provenance[seo.event_id] = existing.event_id
    return list(clustered.values()), provenance


def route_to_questions(
    seos: list[StructuredEvidenceObject], routing_map: dict[str, list[str]]
) -> dict[str, list[StructuredEvidenceObject]]:
    routed: dict[str, list[StructuredEvidenceObject]] = defaultdict(list)
    for seo in seos:
        for question_id, labels in routing_map.items():
            if seo.question_id == question_id or seo.category in labels or seo.claim_type in labels:
                routed[question_id].append(seo)
    return dict(routed)


def _logit(probability: float) -> float:
    clipped = min(max(probability, 1e-6), 1 - 1e-6)
    return math.log(clipped / (1 - clipped))


def _inv_logit(logodds: float) -> float:
    return 1 / (1 + math.exp(-logodds))


def apply_reference_prior(
    reference_class_key: str, priors_table: dict[str, float], epsilon: float = 1e-3
) -> float:
    prior = float(priors_table.get(reference_class_key, priors_table.get("default", 0.5)))
    return min(max(prior, epsilon), 1 - epsilon)


def update_logodds(
    question_id: str,
    current_probability: float,
    evidence: list[StructuredEvidenceObject],
    weights: dict[str, Any],
    last_update_at: datetime | None,
    as_of: datetime,
    historical_event_deltas: dict[str, float] | None = None,
) -> ForecastSnapshot:
    pre_logodds = _logit(current_probability)
    reversals: list[str] = []
    cooldown_active = bool(
        last_update_at
        and as_of - last_update_at < timedelta(hours=float(weights["cooldown_hours"]))
    )

    evidence_deltas: list[float] = []
    cluster_artifacts: dict[str, dict[str, Any]] = {}
    prior = historical_event_deltas or {}
    now = as_of
    for seo in evidence:
        if seo.claim_type == "correction" and seo.correction_of_event_id:
            delta = -prior.get(seo.correction_of_event_id, 0.0)
            evidence_deltas.append(delta)
            reversals.append(seo.correction_of_event_id)
            continue
        base = float(weights["base_by_category"].get(seo.category, 0.0))
        tier_mult = float(weights["source_tier_multiplier"].get(seo.source_tier, 0.5))
        magnitude_mult = {"small": 1.0, "medium": 1.5, "large": 2.0}[seo.magnitude]
        raw_weight = seo.direction * base * tier_mult * magnitude_mult
        cluster_data = aggregate_cluster(
            [raw_weight],
            c_max=float(weights["delta_cap"]),
            tau_hours=float(weights["cooldown_hours"]),
            last_seen_at=None,
            now=now,
        )
        evidence_deltas.append(cluster_data["adjusted_cluster_sum"])
        cluster_artifacts[seo.cluster_id or seo.event_id] = cluster_data

    policy_cfg = {
        "eta": float(weights.get("eta", 1.0)),
        "cap": float(weights["delta_cap"]),
        "saturation": float(weights["saturation"]),
        "cooldown_hours": float(weights["cooldown_hours"]),
    }
    result = update_logodds_policy(pre_logodds, evidence_deltas, policy_cfg, cooldown_active)
    post = float(result.value)
    probability = _inv_logit(post)

    artifacts = {
        "evidence": {
            "raw_llr_sum": result.artifacts["raw_llr_sum"],
            "cluster_sums": cluster_artifacts,
            "cluster_delta_after_sat": result.artifacts["delta_after_saturation"],
            "cooldown_multiplier": result.artifacts["cooldown_multiplier"],
        },
        "caps": {
            "delta_cap_hit": bool(result.artifacts["delta_cap_hit"]),
            "prob_clip_hit": probability in {1e-6, 1 - 1e-6},
        },
    }

    return ForecastSnapshot(
        question_id=question_id,
        as_of=as_of,
        probability=probability,
        logodds=post,
        pre_logodds=pre_logodds,
        delta_logodds=float(result.artifacts["delta_after_saturation"]),
        raw_delta_logodds=float(result.artifacts["raw_llr_sum"]),
        config_version=str(weights["version"]),
        evidence_ids=[item.event_id for item in evidence],
        reversal_of_event_ids=reversals,
        artifacts=artifacts,
    )


def regime_update(
    snapshot: ForecastSnapshot,
    question_id: str,
    regime_signals: dict[str, float],
    regime_params: dict[str, Any],
    enabled: bool,
) -> ForecastSnapshot:
    if not enabled:
        return snapshot
    result = apply_regime_offset(snapshot.logodds, question_id, regime_signals, regime_params)
    adjusted_logodds = float(result.value)
    return ForecastSnapshot(
        question_id=snapshot.question_id,
        as_of=snapshot.as_of,
        probability=_inv_logit(adjusted_logodds),
        logodds=adjusted_logodds,
        pre_logodds=snapshot.pre_logodds,
        delta_logodds=snapshot.delta_logodds,
        raw_delta_logodds=snapshot.raw_delta_logodds,
        config_version=snapshot.config_version,
        evidence_ids=snapshot.evidence_ids,
        regime_adjustment=float(result.artifacts["regime_adjustment"]),
        regime_entropy=float(result.artifacts["regime_entropy"]),
        ablation_label=snapshot.ablation_label,
        reversal_of_event_ids=snapshot.reversal_of_event_ids,
        model_version=snapshot.model_version,
        cal_version=snapshot.cal_version,
        artifacts={
            **snapshot.artifacts,
            "regime": {
                "regime_post": result.artifacts["regime_post"],
                "regime_adjustment": result.artifacts["regime_adjustment"],
                "regime_cap_hit": result.artifacts["regime_cap_hit"],
            },
        },
    )


def monte_carlo(
    initial_price: float,
    target_price: float,
    mu: float,
    sigma: float,
    days: int,
    runs: int,
    seed: int,
) -> float:
    rng = random.Random(seed)
    crossings = 0
    dt = 1.0 / 252.0
    for _ in range(runs):
        price = initial_price
        crossed = False
        for _ in range(days):
            shock = rng.gauss(0.0, 1.0)
            growth = (mu - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * shock
            price *= math.exp(growth)
            if price >= target_price:
                crossed = True
                break
        if crossed:
            crossings += 1
    return crossings / runs


def run_ablation_forecasts(
    baseline: ForecastSnapshot,
    question_id: str,
    regime_signals: dict[str, float],
    regime_params: dict[str, Any],
    mc_probability: float | None = None,
    baseline_features: set[str] | None = None,
    mc_features: set[str] | None = None,
    allow_feature_overlap: bool = False,
    overlap_penalty: float = 0.15,
) -> dict[str, ForecastSnapshot]:
    output = {
        "baseline": ForecastSnapshot(**{**baseline.__dict__, "ablation_label": "baseline"}),
    }
    with_regime = regime_update(baseline, question_id, regime_signals, regime_params, enabled=True)
    output["with_regime"] = ForecastSnapshot(
        **{**with_regime.__dict__, "ablation_label": "+regime"}
    )
    if mc_probability is not None:
        tracker = DependencyTracker()
        tracker.declare_inputs_used("baseline", baseline_features or set())
        tracker.declare_inputs_used("market_path", mc_features or set())
        overlap = tracker.overlap("baseline", "market_path")
        blended, dep_artifacts = dependency_safe_blend(
            with_regime.probability,
            mc_probability,
            overlap,
            allow_overlap=allow_feature_overlap,
            overlap_penalty=overlap_penalty,
        )
        mc_logodds = _logit(blended)
        output["with_regime_mc"] = ForecastSnapshot(
            question_id=with_regime.question_id,
            as_of=with_regime.as_of,
            probability=blended,
            logodds=mc_logodds,
            pre_logodds=with_regime.pre_logodds,
            delta_logodds=mc_logodds - with_regime.pre_logodds,
            config_version=with_regime.config_version,
            evidence_ids=with_regime.evidence_ids,
            raw_delta_logodds=with_regime.raw_delta_logodds,
            regime_adjustment=with_regime.regime_adjustment,
            regime_entropy=with_regime.regime_entropy,
            ablation_label="+regime+mc",
            reversal_of_event_ids=with_regime.reversal_of_event_ids,
            model_version=with_regime.model_version,
            cal_version=with_regime.cal_version,
            artifacts={**with_regime.artifacts, "dependency": dep_artifacts},
        )
    return output
