# ADR-0024 â€” Runtime Family Model

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0005, ADR-0007, ADR-0009, ADR-0010, ADR-0016, ADR-0023, ADR-0025

## Context

After the semantic, binding, phase, and exchange layers are defined, Tigrbl needs a stable runtime classification for units of work.
The architecture pack uses a small runtime-family taxonomy as the normalized execution vocabulary above the ASGI boundary.

## Decision

1. Tigrbl runtime classification is based on a closed family set.
2. The runtime family set is:
   - `request`
   - `session`
   - `message`
   - `stream`
   - `datagram`
3. Runtime families are derived execution concepts; they are not independent programming models.
4. Runtime-family derivation informs execution loops, hook selection extensions, legality checks, and docs/runtime classification where applicable.
5. Binding support may use only this closed family set unless a future ADR expands it.

## Consequences

- Runtime behavior gets a stable normalized vocabulary.
- Transport-specific behaviors can be projected onto one family model.
- Later channel and execution-loop work has a clearer target.
- Hook and legality systems can grow richer without becoming transport-fragmented.

## Rejected alternatives

- Binding-specific family taxonomies.
- Treating runtime families as declarative spec features everywhere.
- Unlimited family growth as new protocols appear.

