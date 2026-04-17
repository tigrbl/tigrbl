# ADR-0028 - Factories Are Canonical Construction Surfaces

- **Status:** Proposed
- **Date:** 2026-04-16
- **Related ADRs:** ADR-0018, ADR-0019, ADR-0027

## Context

The repository currently exposes convenience APIs through both `factories` and `shortcuts`. That boundary only stays coherent if one namespace owns construction helpers and the other acts purely as a convenience re-export layer.

The active line also needs an explicit classification for direct aliases such as `acol`, `vcol`, and `op`.

## Decision

1. `factories` is the canonical owner for construction helpers such as `make*`, `define*`, `derive*`, engine/config builders, response helpers, and direct aliases of those factory functions.
2. `acol`, `vcol`, and `op` are factory aliases because they directly alias factory functions.
3. `shortcuts` remains supported, but only as a thin re-export layer over canonical surfaces.
4. `shortcuts.rest` may re-export REST decorator aliases for convenience, but REST decorators remain owned by the decorators layer rather than the factories layer.
5. Decorator aliases and protocol aliases are not factories and must not be implemented inside `factories`.

## Consequences

- The repository has one canonical construction namespace.
- Convenience imports remain available without confusing ownership.
- Factory aliases are distinguished from op aliases and decorator aliases.

## Rejected alternatives

- Keeping `shortcuts` and `factories` as parallel canonical owners.
- Classifying REST decorators as factories.
- Moving decorator implementations into `factories`.
