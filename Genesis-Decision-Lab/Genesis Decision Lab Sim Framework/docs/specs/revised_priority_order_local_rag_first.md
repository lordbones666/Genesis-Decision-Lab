# Revised Priority Order — Local RAG First, Connectors Later

## Decision

The near-term roadmap prioritizes the reasoning spine and GPT↔backend analytical contracts.
Live-feed OSINT connector farms are explicitly deferred to a later phase.

## What stays in the critical path now

1. Hypothesis management
2. Hidden-state estimation
3. Regime detection
4. Uncertainty decomposition
5. Value-of-information
6. Model arbitration / disagreement
7. Better world-model module layering
8. Stronger GPT ↔ backend communication contracts

## What moves later

- Live source connector sweeps/watchtower
- Broad API-key managed connector expansion
- Large feed maintenance workflows

## Current evidence strategy

Deep research and curated collection feed a growing local corpus:

research/manual collection -> curate -> local RAG corpus -> retrieval -> hypothesis/simulation -> report

## Architecture now

operator + GPT
-> question framing
-> local retrieval corpus
-> hypothesis layer
-> world-model/simulation layer
-> uncertainty + VOI + arbitration
-> report/explanation

## GPT-to-backend contract requirements

### Question objects
Structured fields should include:
- problem_family
- target_domain
- actors
- horizon
- requested_outputs
- comparison_mode
- hypothesis_hints
- missing_information
- uncertainty_posture

### Evidence handoff
Structured fields should include:
- focus summary
- prior context
- evidence themes
- corpus filters

### Analysis contracts
Backend should support:
- branch comparisons
- competing-hypothesis evaluation
- horizon reruns
- variable sensitivity requests
- discriminating signal identification

### Result bundles
Backend should return:
- structured result
- assumptions
- uncertainty status
- traces
- linked hypotheses
- possible next moves
- decision relevance

## Updated phased plan

### Phase 1 (top priority)
Strengthen conversation-to-analysis bridge:
- richer build_question
- richer run_analysis
- richer get_report
- explicit question/result schemas
- GPT decision-rights policy
- adapter translating rich requests to repo execution

### Phase 2
Strengthen reasoning spine:
- hypothesis management
- hidden-state estimator
- regime detector
- uncertainty decomposition
- VOI
- model disagreement layer

### Phase 3
Grow local corpus:
- curated RAG memory
- ingestion from research/docs/notes/PDFs/prior outputs
- method/scenario/evidence archives

### Phase 4 (later)
Selective source intake:
- limited connectors where justified
- optional scraping pipelines
- optional sweep/delta logic
