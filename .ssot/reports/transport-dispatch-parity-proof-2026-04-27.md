# Transport Dispatch Parity Proof

## Context

- Date: 2026-04-27
- SSOT CLI: `.venv/Scripts/ssot.exe`
- Target feature: `feat:transport-parity-contract-001`
- Related endpoint-key feature: `feat:jsonrpc-endpoint-key-001`

## Verified Commands

```text
.venv\Scripts\python.exe -m pytest pkgs\core\tigrbl_core\tests\test_jsonrpc_endpoint_binding_spec_contract.py pkgs\core\tigrbl_tests\tests\unit\test_transport_dispatch_parity_contract.py -q --basetemp .tmp\pytest-transport-contracts
```

Result: `2 passed`.

```text
.venv\Scripts\python.exe -m pytest pkgs\core\tigrbl_tests\tests\parity\test_executor_metamorphic_parity.py pkgs\core\tigrbl_tests\tests\harness_v3\test_uvicorn_e2e_appspec.py -q --basetemp .tmp\pytest-transport-existing-proof
```

Result: `2 passed`.

## Proof Summary

The placeholder transport parity contract was replaced with an executable test
that creates data through REST, reads it through JSON-RPC, creates data through
JSON-RPC, reads it through REST, and confirms both surfaces return the same
list projection after binding materialization.

The endpoint-keyed JSON-RPC contract was also converted from a placeholder into
an executable core spec test. It verifies the default endpoint identity,
core-owned default endpoint mapping, explicit endpoint keys, and AppSpec
serialization round-trip behavior.

## SSOT Updates

- `tst:transport-dispatch-parity-contract` is `passing`.
- `evd:transport-dispatch-parity-test` is `passed`.
- `clm:transport-parity-contract-001` is `evidenced`.
- `feat:transport-parity-contract-001` is `implemented`.
- `tst:jsonrpc-endpoint-binding-contract` is `passing`.
- `evd:transport-dispatch-jsonrpc-test` is `passed`.
- `clm:jsonrpc-endpoint-key-001` is `evidenced`.

## Remaining Scope

This proof closes the semantic parity contract row. It does not close the wider
runtime protocol profile. Remaining non-passing rows include binding-driven
ingress, BindingSpec-to-KernelPlan protocol compilation, executor dispatch
removal, KernelPlan dispatch ownership, transport bypass removal, OpenRPC/REST
helper surfaces, JSON-RPC batch and notification behavior, and Python/Rust ASGI
boundary evidence.
