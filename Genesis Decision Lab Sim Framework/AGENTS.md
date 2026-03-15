
# AGENTS.md

## Scope

This repo/worktree contains the retrieval substrate workstream for the Decision Lab seed.

Your scope is limited to:

- `config/**`
- `docs/**`
- `src/retrieval/**`
- `tests/**`
- `README.md`
- this `AGENTS.md`

Do not modify simulation, forecasting, or orchestration code outside this scope unless a ticket explicitly authorizes it.

---

## Mission

Build a small, trustworthy retrieval substrate that provides:
- ingestion
- chunking
- metadata/provenance
- retrieval contracts
- retrieval evaluation

This workstream supports the Abacus-based Decision Lab seed, but it is not the world model and it is not the orchestrator.

---

## Required workflow

Always work in this order:

1. Plan
2. Implement
3. Verify

Start from the contract. Then ingest. Then retrieve. Then evaluate.

---

## Non-negotiable rules

### 1) Retrieval is support, not world modeling
Do not describe this layer as the world model.
Do not put causal reasoning or simulation logic into retrieval.

### 2) Provenance is mandatory
Every retrieval result must include enough provenance to understand:
- where it came from
- what file/source it belongs to
- what chunk it is
- any important timestamps/labels available

### 3) Keep the interface narrow
Build one clean retrieval contract for upstream consumption.
Do not build broad platform abstractions.

### 4) Keep chunking simple and testable
Use stable chunk IDs and ordering.
Do not invent complex adaptive chunking unless required.

### 5) Do not modify Abacus simulation logic
This workstream is separate on purpose.
Do not edit simulation/forecasting modules unless explicitly authorized.

### 6) No memory hype
Do not market this as memory, selfhood, or a world model.
It is retrieval infrastructure.

### 7) Every new file must justify itself
Add only files needed for:
- contracts
- ingestion
- indexing/query
- metadata/provenance
- tests
- minimal docs

### 8) Stop on ambiguity
If source formats, corpus boundaries, or contract semantics are unclear, create `docs/questions.md` and stop. Do not guess.

---

## Style rules

- Keep names literal and operational.
- Prefer plain data contracts over magical abstractions.
- Prefer small modules over framework sprawl.
- Keep docs short and executable.

---

## Output discipline

When you finish:
- update README if user-facing behavior changed
- add or adjust tests
- document one end-to-end ingestion plus retrieval path
- summarize what changed and why

---

## Verification standard

A task is not done until:
- contracts are clear
- ingestion works on a small curated corpus
- retrieval returns provenance-backed results
- tests pass
- no unrelated repo drift was introduced

---

## Approval gates

Ask before:
- renaming files
- moving directories
- changing package boundaries
- adding many new abstractions
- modifying code outside the allowed scope

---

## Build posture

Prefer:
- boring infrastructure
- typed contracts
- explicit provenance
- additive changes
- small reproducible evals

Avoid:
- platform sprawl
- dashboard-first work
- giant schema systems
- mixing generated content with source truth without labels
- vendor lock-in where avoidable
