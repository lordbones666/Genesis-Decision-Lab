# World Model Framework Expansion Map

**As-of:** 2026-03-15  
**Purpose:** This document defines the next expansion path for the Decision Lab / Abacus world-model stack.

It is **not** a proposal for one giant universal model.  
It is a map of framework families that can become callable, testable modules inside the system.

**Core doctrine:**
- build a portfolio of modeling frameworks
- route by problem family
- preserve explicit assumptions
- keep domains of validity visible
- use the smallest adequate model first
- treat disagreement between models as information

---

## System Goal

The world-model stack should answer questions of this form:
- What state is the world likely in right now?
- How does that state evolve over time?
- What propagates if X changes?
- What threshold is likely to be crossed?
- How do strategic actors respond?
- What uncertainty matters most for the decision?
- What information would most improve the decision?

---

## Canonical Modeling Layers

### Layer 1 — Observation / Evidence Layer

**Purpose:**
- ingest evidence
- normalize claims
- weight source quality
- update beliefs

**Typical inputs:**
- claims
- events
- measurements
- source metadata
- timestamps
- contradiction signals

**Typical outputs:**
- weighted evidence record
- likelihood ratios
- posterior update inputs
- evidence confidence bands

**Current strength:**
- already partially present in the system

**Recommended methods:**
- Bayesian evidence update
- source reliability priors
- contradiction scoring
- hierarchical evidence weighting

---

### Layer 2 — Hidden State Estimation Layer

**Purpose:** infer latent conditions not directly observed.

**Examples:**
- institutional brittleness
- supply chain fragility
- war escalation posture
- regime stability
- credit stress
- social unrest potential

**Typical inputs:**
- observed indicators over time
- evidence updates
- transition assumptions
- prior state probabilities

**Typical outputs:**
- posterior state estimate
- hidden state probabilities
- regime candidate distribution
- confidence intervals

**Recommended methods:**
- Hidden Markov Models
- Switching State-Space Models
- Kalman Filters
- Particle Filters
- Bayesian latent-state estimation

**Why it matters:** Most real-world forecasting errors come from skipping hidden-state estimation and going straight from observation to prediction.

**Priority:** Very high

---

### Layer 3 — Transition / Temporal Evolution Layer

**Purpose:** model how states evolve over time.

**Typical inputs:**
- current state estimate
- transition assumptions
- exogenous shock conditions
- temporal horizon

**Typical outputs:**
- future state paths
- transition probabilities
- regime transition likelihoods
- failure or persistence estimates

**Recommended methods:**
- Markov transition matrices
- regime-switching models
- hazard models
- survival analysis
- drift/volatility processes
- jump processes
- Bayesian online change-point detection

**Priority:** Very high

---

### Layer 4 — Causal / Structural Layer

**Purpose:** model how interventions or changes propagate through the system.

**Typical inputs:**
- structural graph
- intervention choice
- causal assumptions
- node state values

**Typical outputs:**
- downstream effects
- intervention forecast
- counterfactual estimate
- causal sensitivity map

**Recommended methods:**
- Directed acyclic graphs
- structural equation models
- Bayesian networks
- intervention logic
- counterfactual propagation
- constraint-based causal structures

**Why it matters:** This is the difference between describing the world and reasoning about what changes it.

**Priority:** High

---

### Layer 5 — Network / Contagion Layer

**Purpose:** model spread, cascades, and dependency propagation.

**Typical domains:**
- supply chains
- finance
- sanctions/trade
- migration spillover
- conflict escalation
- infrastructure dependencies

**Typical inputs:**
- network topology
- node states
- edge weights
- contagion thresholds
- failure probabilities

**Typical outputs:**
- cascade likelihoods
- bottleneck map
- contagion path probabilities
- critical node ranking

**Recommended methods:**
- weighted directed graphs
- threshold contagion models
- percolation logic
- cascade failure models
- network diffusion
- multiplex network propagation

**Priority:** High

---

### Layer 6 — Actor / Strategy Layer

**Purpose:** model adaptive behavior by governments, firms, institutions, factions, or other strategic actors.

**Typical inputs:**
- actor incentives
- constraints
- current state
- signaling conditions
- adversarial assumptions

**Typical outputs:**
- probable actor responses
- strategic branches
- payoff-sensitive scenario trees
- adversarial risk map

**Recommended methods:**
- game-theoretic approximations
- policy reaction functions
- signaling models
- bounded rationality models
- agent-based simulation
- minimax or adversarial branches

**Why it matters:** Most forecasting systems under-model adaptation. Real systems react.

**Priority:** High

---

### Layer 7 — Threshold / Risk Layer

**Purpose:** estimate barrier crossing, failure probabilities, extreme moves, and time-to-event risk.

**Typical inputs:**
- state estimate
- volatility or drift assumptions
- threshold values
- horizon
- exogenous shock scenarios

**Typical outputs:**
- crossing probability
- time-to-threshold distribution
- tail risk estimate
- hazard rate

**Recommended methods:**
- Monte Carlo threshold simulation
- first-passage approximations
- survival or hazard models
- extreme value theory
- stochastic process approximations

**Current strength:** partially present through Monte Carlo and threshold logic.

**Priority:** Medium to high

---

### Layer 8 — Scenario Generation Layer

**Purpose:** construct structured possible futures rather than one-point outputs.

**Typical inputs:**
- current state
- actor assumptions
- exogenous shock choices
- uncertainty decomposition

**Typical outputs:**
- scenario tree
- branch assumptions
- branch probabilities
- scenario comparison bundle

**Recommended methods:**
- scenario trees
- branching simulation
- influence diagrams
- structured alternative futures
- branch pruning logic

**Priority:** Medium to high

---

### Layer 9 — Uncertainty Decomposition Layer

**Purpose:** determine which uncertainties matter most and why.

**Typical inputs:**
- model outputs
- parameter uncertainty
- scenario uncertainty
- structural uncertainty
- model disagreement

**Typical outputs:**
- uncertainty importance ranking
- dominant uncertainty sources
- confidence decomposition
- decision sensitivity map

**Recommended methods:**
- variance decomposition
- local/global sensitivity analysis
- entropy reduction
- posterior variance attribution
- model disagreement tracking

**Why it matters:** The useful question is not only what is uncertain, but which uncertainty changes the decision.

**Priority:** Very high

---

### Layer 10 — Decision / Value-of-Information Layer

**Purpose:** turn world-model output into decision support.

**Typical inputs:**
- scenario outputs
- uncertainty decomposition
- action set
- payoff or regret assumptions

**Typical outputs:**
- recommended next action
- decision threshold crossing
- value of more information
- robust decision comparison
- regret table

**Recommended methods:**
- expected value or expected utility
- regret minimization
- robust optimization
- EVPI or EVPPI
- sensitivity-weighted decision logic
- proper scoring rule integration

**Priority:** Very high

---

## Canonical Expansion Set (Recommended First 12)

### 1) Bayesian Evidence Update
**Problem family:** update beliefs with new evidence  
**Math family:** Bayesian updating, likelihood ratios, hierarchical reliability priors  
**Inputs:** prior, evidence items, source reliability, contradiction factors  
**Outputs:** posterior estimate, evidence contribution table  
**Priority:** Already canonical; extend

---

### 2) Hidden-State Estimator
**Problem family:** infer latent system condition  
**Math family:** HMM, particle filter, switching state-space model  
**Inputs:** observed indicators, prior state distribution, transition assumptions  
**Outputs:** latent state distribution, most likely hidden state, confidence band  
**Priority:** Build next

---

### 3) Regime Detector
**Problem family:** detect whether the governing process has changed  
**Math family:** online change-point detection, regime-switching models, HMM classification  
**Inputs:** time series, indicator panel, recent shocks  
**Outputs:** regime label, change probability, model-selection hint  
**Priority:** Build next

---

### 4) Monte Carlo Threshold / Path Engine
**Problem family:** estimate path and crossing probabilities  
**Math family:** Monte Carlo simulation, stochastic path generation  
**Inputs:** current state, drift or volatility assumptions, threshold, horizon, seed or run count  
**Outputs:** crossing probability, path summaries, percentile distribution  
**Priority:** Already canonical; extend

---

### 5) Structural Causal Graph
**Problem family:** reason about interventions and downstream effects  
**Math family:** DAGs, structural equations, intervention logic  
**Inputs:** causal graph, intervention node, current values  
**Outputs:** downstream changes, counterfactual path, causal sensitivity summary  
**Priority:** Build after regime and state modules

---

### 6) Network Contagion / Dependency Propagation
**Problem family:** model cascades across connected systems  
**Math family:** weighted graphs, threshold contagion, cascade logic  
**Inputs:** node states, edge weights, trigger event, cascade rules  
**Outputs:** propagation paths, critical nodes, cascade likelihood  
**Priority:** Build soon

---

### 7) Actor-Response Simulator
**Problem family:** model strategic response  
**Math family:** game-theory approximations, reaction functions, bounded-rationality agent simulation  
**Inputs:** actor set, incentives, constraints, current state, trigger event  
**Outputs:** actor action probabilities, branch set, strategic scenario summary  
**Priority:** Build soon

---

### 8) Hazard / Failure Model
**Problem family:** estimate time-to-failure or event risk  
**Math family:** hazard models, survival analysis, time-to-event estimation  
**Inputs:** state estimate, stress indicators, horizon  
**Outputs:** hazard rate, survival curve, event probability by horizon  
**Priority:** Medium-high

---

### 9) Scenario Tree Generator
**Problem family:** generate plausible future branches  
**Math family:** branching logic, scenario probability trees, influence diagrams  
**Inputs:** current state, key uncertainty drivers, actor branches, regime assumptions  
**Outputs:** scenario tree, branch assumptions, branch probabilities  
**Priority:** Medium-high

---

### 10) Sensitivity / Uncertainty Decomposition Engine
**Problem family:** find what matters most  
**Math family:** sensitivity analysis, variance decomposition, entropy reduction  
**Inputs:** model outputs, uncertain parameters, structural assumptions  
**Outputs:** ranked uncertainty drivers, sensitivity map, confidence decomposition  
**Priority:** Build soon

---

### 11) Value-of-Information Module
**Problem family:** determine what information is worth acquiring next  
**Math family:** EVPI, EVPPI, entropy reduction, decision threshold shift analysis  
**Inputs:** current decision, uncertainty decomposition, action payoffs or regret rules  
**Outputs:** highest-value information targets, VOI score, recommended next data collection  
**Priority:** Build soon

---

### 12) Model Arbitration / Ensemble Disagreement Layer
**Problem family:** compare multiple model outputs and use disagreement as signal  
**Math family:** ensemble weighting, disagreement metrics, confidence arbitration logic  
**Inputs:** outputs from multiple modules, calibration metadata, domain validity signals  
**Outputs:** combined estimate, disagreement score, regime or mismatch warning, arbitration rationale

**Why it matters:** Model disagreement is not only a nuisance. It is often a structural signal.

**Priority:** Build soon

---

## Underused but High-Leverage Directions

### A) Forecasting via hidden-state estimation first
Instead of: evidence to forecast  
Use: evidence to hidden state to transition to forecast

This is a major quality upgrade.

---

### B) Model disagreement as information
Do not only average models.

Track:
- where they disagree
- when they disagree
- which assumptions create divergence

This can reveal:
- regime instability
- structural mismatch
- high-information zones

---

### C) Decision-focused uncertainty
Rank uncertainty not by raw size, but by how much it changes the decision.

---

### D) Intervention / counterfactual logic
Move beyond prediction into:
- what if we intervene?
- what if this had not happened?
- what is structurally causal?

---

### E) Actor adaptation loops
Do not treat the world as passive.

Build modules that ask:
- how do actors react to forecasts, policies, shocks, and each other?

---

## Development Pattern for New Modules

Every new framework should be built in this order.

1. **Define the problem family** (e.g., threshold crossing, contagion spread, regime transition, strategic actor response, hidden-state estimation)
2. **Define the state variables** (observed variables, hidden variables, controls, exogenous shocks, actor variables)
3. **Choose the smallest adequate model family**
4. **Define the module contract** (purpose, domain of validity, assumptions, required inputs, output schema, uncertainty behavior, failure modes)
5. **Build as callable module** (typed contracts, replay support, tests, scenario examples, uncertainty status)
6. **Evaluate** (calibration, stability, sensitivity, misuse risk, comparison to simpler baselines)

---

## Priority Order for Buildout

### Tier 1 — Immediate expansion
- Hidden-State Estimator
- Regime Detector
- Uncertainty Decomposition Engine
- Value-of-Information Module

**Why:** These dramatically improve the quality of everything else.

---

### Tier 2 — Strategic and propagation expansion
- Structural Causal Graph
- Network Contagion / Dependency Propagation
- Actor-Response Simulator
- Model Arbitration / Disagreement Layer

**Why:** These move the system from forecasting toward realistic world reasoning.

---

### Tier 3 — Scenario and risk refinement
- Hazard / Failure Model
- Scenario Tree Generator
- Extreme risk and tail-model refinements
- Domain-specialized actor or contagion variants

**Why:** These refine the practical analytical surface after the state, causal, and actor base is stronger.

---

## Recommended Canon Policy

Maintain three classes of frameworks.

### Canonical Core
- 8 to 12 modules
- most used
- heavily tested
- routed to often
- strongly documented

### Specialized Modules
- 10 to 20 modules
- domain-specific
- invoked when fit is clear
- narrower validity range

### Experimental Modules
- many possible
- sandboxed
- opt-in
- not routed to by default
- promoted only after evaluation

---

## Practical Conclusion

The next major expansion should focus less on adding more raw simulators and more on adding:
- hidden-state estimation
- regime awareness
- structural causal logic
- actor-response simulation
- uncertainty decomposition
- value-of-information
- model disagreement as signal

Those are the upgrades most likely to make the system feel materially more advanced rather than merely broader.

The strongest architectural shift is this:

> Do not forecast directly from observations whenever hidden state matters. Infer latent state first, then model transitions, then evaluate decisions.
