# GPT Decision-Rights Policy

## Purpose

Define responsibility boundaries between GPT/operator intent and backend execution authority.

## GPT / Operator may decide

- analysis strategy and sequencing
- question framing and comparison mode
- whether to retrieve first or simulate first
- whether to request clarification
- hypothesis hints and discriminating-signal focus
- report style and narrative emphasis

## Backend must decide

- final tool routing and payload validation
- parameter coercion and safety checks
- uncertainty status (`valid`, `partial`, `out_of_domain`)
- trace identifiers and ledger references
- method-specific execution details
- assumption and failure-mode reporting

## Requires operator confirmation

- expensive reruns or large scenario sweeps
- partial-domain outputs used for external decisions
- assumption-heavy reruns from stale trace context
- conflicting model-arbitration outputs with high disagreement

## Enforcement notes

- GPT guidance is strategic; backend remains authoritative for execution semantics.
- No automatic escalation to live-source connector architecture.
- Local-RAG evidence handoff remains default evidence path.
