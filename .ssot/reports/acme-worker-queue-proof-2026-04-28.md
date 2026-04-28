# ACME Worker Queue Proof

Generated: 2026-04-28

## Certification Gap Review

The current registry validates structurally, but the active certification line is
not fully conformant because active profiles still contain partial or absent
feature rows, legacy frozen-boundary claims are not linked to feature rows, and
release-blocking issues and risks remain open.

Live SSOT counts before this closure slice:

- Features: 592 total; 229 implemented, 282 partial, 81 absent.
- Claims: 246 total; 18 claims without linked features.
- Profiles: 6 active profiles with non-implemented rows.
- Open release-blocking issues: `iss:active-line-certification-closure-blocked-001`,
  `iss:certifiable-package-proof-chain-gap-001`.
- Active release-blocking risks: `rsk:active-line-nonimplemented-feature-claims-001`,
  `rsk:profileless-certification-scope-001`,
  `rsk:unverified-package-proof-chain-001`.

Profile blockers before this closure slice:

- `prf:tigrbl-active-line-certification-closure`: 160 implemented, 7 partial, 13 absent.
- `prf:tigrbl-public-operator-surface`: 26 implemented, 65 partial, 4 absent.
- `prf:tigrbl-extension-and-plugin-surface`: 15 implemented, 113 partial, 13 absent.
- `prf:tigrbl-runtime-protocol-conformance`: 11 implemented, 41 partial, 25 absent.
- `prf:tigrbl-production-hardening`: 34 implemented, 24 partial, 12 absent.
- `prf:tigrbl-development-governance`: 39 implemented, 26 partial, 7 absent.

Concrete incomplete files observed in this review include:

- `pkgs/apps/tigrbl_acme_ca/tigrbl_acme_ca/workers/queue.py`: previously had no
  bounded operational queue behavior or proof tests.
- `pkgs/apps/tigrbl_spiffe/src/tigrbl_spiffe/identity/svid_validator.py`: still
  documents placeholder cryptographic validation behavior.
- `pkgs/engines/tigrbl_engine_clickhouse/src/tigrbl_engine_clickhouse/session.py`:
  still contains intentional unsupported transaction/session branches.
- `pkgs/core/tigrbl_tests/tests/unit/test_transport_dispatch_parity_contract.py`:
  currently records a skipped governance placeholder for shared dispatch parity.

## Delivery Plan

1. Close active proof-chain mechanics first: eliminate unlinked claim warnings,
   ensure every active profile feature has claim/test/evidence edges, and keep
   each claim status below certified until executable evidence exists.
2. Close operational queue and backpressure surfaces: make runtime queues
   bounded, observable, timeout-aware, and covered by focused tests across ACME,
   callback, webhook, and transport queues.
3. Close extension/plugin hardening gaps: replace placeholder SPIFFE SVID
   validation, ACME key-provider behavior, and adapter-only proof with
   executable validation and failure-mode tests.
4. Close runtime protocol conformance gaps: replace skipped shared-dispatch
   placeholders with passing REST, JSON-RPC, WebSocket, stream, and SSE contract
   tests that exercise the shared transport path.
5. Close production hardening gaps: prove negative auth, schema, persistence,
   observability, queue overflow, and external dependency failure behavior.
6. Close development governance gaps: ensure package-coordinate tests,
   buildability/importability gates, ADR/SPEC hash checks, and registry
   validation are mandatory certification evidence.
7. Certify the active line only after every active profile evaluates cleanly, no
   release-blocking issue or risk remains open, and release evidence references
   concrete passing command output.

## Implemented Closure Slice

`pkgs/apps/tigrbl_acme_ca/tigrbl_acme_ca/workers/queue.py` now provides:

- bounded in-memory queue capacity via `max_items`;
- enqueue timeout support using `asyncio.wait_for`;
- dequeue timeout behavior returning `None`;
- observable `size`, `max_items`, and `closed` state;
- explicit close semantics that reject new work while allowing existing items to
  drain;
- `from_ctx` config support through `acme.task_queue_max_items`.

Focused proof command:

```text
.\.venv\Scripts\python.exe -m pytest pkgs\apps\tigrbl_acme_ca\tests\test_worker_queue.py -q --basetemp .tmp\pytest-acme-worker-queue
```

Result:

```text
5 passed in 0.07s
```
