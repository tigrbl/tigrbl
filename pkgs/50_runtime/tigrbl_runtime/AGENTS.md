# tigrbl-runtime Boundary

Do not add behavior to `tigrbl_runtime` by default.

Before editing this package, prove why the change cannot live in:

1. `tigrbl_kernel` for plan construction, route/protocol selection, legality, and fallback selection.
2. `tigrbl_atoms` for phase behavior, dispatch parsing, egress shaping, response envelopes, and transport atoms.
3. `tigrbl_ops_*` for operation behavior.

Runtime changes are allowed only for executing compiled kernel plans, preserving runtime context compatibility, or maintaining already-declared carrier lifecycle bridges.

Do not add executors, response emission logic, protocol policy, route matching semantics, or new modules.
