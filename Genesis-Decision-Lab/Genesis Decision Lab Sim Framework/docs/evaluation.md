# Evaluation Methodology

- Score binary outcomes with Brier score.
- Build calibration bins by domain × horizon.
- Fit temperature scaling alpha on strictly past data only.
- Enforce no leakage with time-split tests.
