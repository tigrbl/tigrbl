# Transport Dispatch KernelPlan Proof

Run time: 2026-04-28T00:04:22.3256834-05:00

## Scope

This proof covers the governed transport dispatch target where compiled KernelPlan data owns HTTP REST and JSON-RPC selector lookup.

Linked SSOT rows:

- Feature: `feat:kernelplan-dispatch-ownership-001`
- Feature: `feat:transport-bypass-removal-001`
- Feature: `feat:executor-dispatch-removal-001`
- Test: `tst:transport-dispatch-kernelplan-contract`
- Claim: `clm:kernelplan-dispatch-ownership-001`
- Evidence: `evd:transport-dispatch-kernelplan-test`

## Result

The placeholder test in `pkgs/core/tigrbl_kernel/tests/test_transport_dispatch_kernelplan_contract.py` was converted into an executable contract. It now proves that `_compile_plan` writes REST and JSON-RPC transport selectors into `KernelPlan.opkey_to_meta` and `KernelPlan.proto_indices`, including exact REST routes, templated REST routes, JSON-RPC endpoint buckets, and selector metadata.

Verification command:

```text
$env:UV_CACHE_DIR='.uv-cache'; uv run pytest pkgs/core/tigrbl_kernel/tests/test_transport_dispatch_kernelplan_contract.py pkgs/core/tigrbl_tests/tests/unit/test_transport_dispatch_parity_contract.py -q --basetemp .tmp\pytest-transport-dispatch-proof
```

Observed result:

```text
2 passed in 0.28s
```

## Remaining Gap

This proof does not close the full transport-dispatch lane. The runtime still contains executor-side program resolution fallback paths, so these feature rows should remain `partial` until executor dispatch removal, bypass removal, and Rust/Python lane parity are completed and certified.

## Delivery Plan

1. Close current and explicit targets first because they are the certifiable release line.
2. Convert skipped or planned tests for next-target transport dispatch into executable contracts where code already satisfies the contract.
3. Remove executor-side transport matching only after KernelPlan and atom lookup paths have complete REST, JSON-RPC, stream, websocket, and webtransport coverage.
4. Populate active certification profiles with feature memberships so profile evaluation has real scope.
5. Add or link claims, tests, and evidence for every current, explicit, and next target that lacks a proof chain.
6. Run `registry sync-statuses --dry-run`, then `registry sync-statuses`, then `validate --write-report` after each closure batch.
7. Promote only rows with passing tests and concrete evidence; leave runtime and Rust optimization rows absent until implementation exists.
