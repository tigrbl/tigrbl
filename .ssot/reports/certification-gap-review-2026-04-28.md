# Certification Gap Review

Run time: 2026-04-28T04:05:49.4143069-05:00

## Current SSOT State

- Features: 592 total; 229 implemented, 282 partial, 81 absent.
- Profiles: 6 active profiles.
- Issues: 2 open release-blocking issues.
- Risks: 3 active release-blocking risks.
- SSOT validation: passed with warnings.

## Blocking Issues

- `iss:active-line-certification-closure-blocked-001`
- `iss:certifiable-package-proof-chain-gap-001`

## Active Risks

- `rsk:active-line-nonimplemented-feature-claims-001`
- `rsk:profileless-certification-scope-001`
- `rsk:unverified-package-proof-chain-001`

## Profile Gaps

| Profile | Implemented | Partial | Absent |
| --- | ---: | ---: | ---: |
| `prf:tigrbl-active-line-certification-closure` | 160 | 7 | 13 |
| `prf:tigrbl-public-operator-surface` | 26 | 65 | 4 |
| `prf:tigrbl-extension-and-plugin-surface` | 15 | 113 | 13 |
| `prf:tigrbl-runtime-protocol-conformance` | 11 | 41 | 25 |
| `prf:tigrbl-production-hardening` | 34 | 24 | 12 |
| `prf:tigrbl-development-governance` | 39 | 26 | 7 |

## Delivery Plan

1. Close active certification targets.
   - Finish next-target runtime and production evidence rows in the active-line certification profile.
   - Keep blocked claims blocked until linked passing evidence exists.

2. Close runtime protocol conformance.
   - Implement or explicitly descope absent transport runtime rows.
   - Prioritize transport event registry, WebTransport events, protocol scope schemas, accept/emit/close atoms, SSE chains, WebSocket chains, and Rust protocol plan parity.

3. Close public operator behavior.
   - Finish SSE, WebSocket/WSS, static-file runtime chains, upload/file runtime contracts, and server support claim links.
   - Keep supported server proof limited to actual supported servers.

4. Close extension and plugin capability proof.
   - Convert surface inventory rows from partial to implemented only when runtime behavior, docs projection, tests, and evidence all exist.
   - Continue row-per-extension proof for hooks, middleware, engine plugins, docs helpers, diagnostics, and SPIFFE/ACME app surfaces.

5. Close production hardening.
   - Prove request hot path DDL exclusion, schema readiness fail-closed behavior, transaction boundary evidence, and benchmark baselines.
   - Keep Python and Rust lanes separate until each lane has direct proof.

6. Close governance and release proof.
   - Link legacy frozen/blocked claims where appropriate or retain them as documented warnings.
   - Re-run SSOT validation, focused tests, package build/import smoke, and release gate validators before promotion.

## Work Completed In This Run

- Implemented `tigrbl_spiffe.tls.adapters.httpx_client_with_tls` so it passes the TLS helper SSL context into `httpx.AsyncClient`.
- Added a focused adapter contract test.
- Created and linked:
  - `feat:spiffe-httpx-tls-context-adapter-001`
  - `clm:spiffe-httpx-tls-context-adapter-001`
  - `tst:spiffe-httpx-tls-context-adapter-contract`
  - `evd:spiffe-httpx-tls-context-adapter-proof-20260428`
- Added the feature to `prf:tigrbl-extension-and-plugin-surface`.

## Verification

```text
.\.venv\Scripts\python.exe -m pytest pkgs\apps\tigrbl_spiffe\tests\test_adapters.py -q --basetemp .tmp\pytest-spiffe-tls-adapter-final
5 passed in 0.74s

.\.venv\Scripts\ssot.exe validate . --write-report
passed: true
```
