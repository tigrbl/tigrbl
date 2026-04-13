# Gate C: Conformance Security

## Objective

Prove the retained spec/security claims with aligned docs, emitted behavior, runtime semantics, and negative tests.

## Status

Passed in the Phase 11 checkpoint.

## What Gate C proves in this checkpoint

The Phase 11 checkpoint proves that the retained exact spec/security claim set is closed at checkpoint quality:

- OpenAPI 3.1 docs and emitted behavior are aligned
- explicit JSON Schema Draft 2020-12 behavior is present and tested
- JSON-RPC 2.0 is explicit and tested
- OpenRPC 1.2.6 is explicit and tested
- retained exact RFC auth rows are tested
- OAS security-scheme docs and runtime semantics are aligned
- negative/security tests are included and mapped in the evidence registry

## Retained exact claim set proved here

- `OAS-001` through `OAS-006`
- `SEC-001` through `SEC-006`
- `RPC-001` through `RPC-003`
- `RFC-7235`
- `RFC-7617`
- `RFC-6750`

## Explicitly de-scoped exact rows carried forward

The broader exact OAuth/OIDC/JWT/PKCE/metadata/mTLS/DPoP rows remain explicitly de-scoped from the current cycle:

- `OIDC-001`
- `RFC-6749`
- `RFC-7519`
- `RFC-7636`
- `RFC-8414`
- `RFC-8705`
- `RFC-9110`
- `RFC-9449`

## Machine-checked proof surfaces

- validator: `tools/ci/validate_gate_c_conformance_security.py`
- validator tests: `tools/ci/tests/test_gate_c_conformance_security.py`
- workflow: `.github/workflows/gate-c-conformance-security.yml`
- evidence map: `docs/conformance/RFC_SECURITY_EVIDENCE_MAP.md`
- dev gate-result: `docs/conformance/dev/0.3.18.dev1/gate-results/gate-c-conformance-security.md`
- historical release gate-result: `docs/conformance/releases/0.3.17/gate-results/gate-c-conformance-security.md`
- promoted release gate-result: `docs/conformance/releases/0.3.18/gate-results/gate-c-conformance-security.md`

## Position after later gates

Gate D reproducibility and Gate E promotion are now also passed for the promoted release `0.3.18`.
