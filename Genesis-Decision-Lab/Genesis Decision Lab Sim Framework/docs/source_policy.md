# Source Policy and Tiering

- Tier 1: primary/official data sources.
- Tier 2: high-quality wires and established outlets.
- Tier 3: commentary and lower-authority sources.

UI should show source tier badge (`T1`, `T2`, `T3`) with one-line explanation: "T1 is primary evidence, T2 is strong secondary corroboration, T3 is contextual/non-primary."

All source records require URL, retrieval timestamp, publisher, and title when available.
For replay, SRs also include `content_hash`, `excerpt`, and optional `archive_pointer`.
