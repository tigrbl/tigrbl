# Canonical Factories and Shortcut Re-Exports

﻿
Date: 2026-04-16
Kind: repo-local

## Intent

This document defines the canonical ownership boundary for `factories` and `shortcuts`.

## Canonical model

- `factories` is the canonical owner for:
  - `make*`
  - `define*`
  - `derive*`
  - engine/config builders
  - response helpers
  - direct aliases of factory functions such as `acol`, `vcol`, and `op`
- `shortcuts` is a convenience re-export layer over canonical surfaces.
- `shortcuts.rest` may re-export REST decorator aliases, but those decorators remain owned by the decorators layer.

## Classification rules

- `acol` is a factory alias because it aliases `makeColumn`.
- `vcol` is a factory alias because it aliases `makeVirtualColumn`.
- `op` is a factory alias because it aliases the canonical op factory.
- Decorator aliases and protocol aliases are not factories.

## Traceability

- ADR: `.ssot/adr/ADR-1029-factories-are-canonical-construction-surfaces.md`
- Tests:
  - `pkgs/core/tigrbl_tests/tests/unit/test_http_route_registration.py`
