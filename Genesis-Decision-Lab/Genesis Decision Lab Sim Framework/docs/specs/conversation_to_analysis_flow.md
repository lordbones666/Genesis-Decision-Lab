# Conversation-to-Analysis Flow (Local-RAG-First)

## Flow

1. Operator/GPT creates structured `QuestionObject` and `EvidenceHandoff`.
2. Adapter builds `AnalysisRequest` and forwards to orchestration runner.
3. Runner selects first-class world-model tool via manifest-routable mapping.
4. World-model bridge executes tool and returns `WorldModelResult` with uncertainty + trace.
5. Hypothesis manager links competing hypotheses and evidence support/contradiction.
6. Adapter emits `AnalysisResultBundle` with assumptions, uncertainty, hypotheses, next moves.
7. Report builder emits decision-oriented `DecisionReport`.

## Explicit non-goals (current phase)

- live source connector farm
- sweep/watchtower pipelines
- API-key maintenance architecture

## Evidence path

curated research -> local corpus -> retrieval context -> analysis request -> simulation/reasoning -> report
