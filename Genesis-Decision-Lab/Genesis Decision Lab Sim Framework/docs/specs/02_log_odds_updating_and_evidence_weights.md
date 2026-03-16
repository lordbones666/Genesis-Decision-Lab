# Log-Odds Updating & Evidence Weights

Additive log-odds updates are treated as LLR-like increments with engineering robustness guards:
- tempering/shrinkage concepts
- delta caps and saturation
- raw vs processed delta persistence for auditability
- strict dedupe constraints before additive pooling
