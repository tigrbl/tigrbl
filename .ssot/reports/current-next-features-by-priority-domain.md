# Current And Next Features By Priority And Domain

Source: .ssot/registry.json
Generated: 2026-04-27T12:46:48Z

Priority is plan.horizon. Domain is plan.slot when present, otherwise inferred from linked SPEC number family.
Total current/next features: 210

## Priority: current (155)

### Domain: appspec-corpus (2)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:appspec-corpus-canonical-fixture-001` | AppSpec canonical corpus fixture | `implemented` | `active` | T2 | spc:2082, spc:2090 | 3 | 2 |
| `feat:appspec-corpus-negative-fail-closed-001` | AppSpec negative corpus fail-closed lane | `implemented` | `active` | T2 | spc:2082, spc:2090 | 3 | 2 |

### Domain: authn-provider-integration-status (1)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:authn-provider-missing-credentials-status-001` | AuthN provider missing-credential status projection | `implemented` | `active` | T2 | spc:2012, spc:2080, spc:2090 | 4 | 3 |

### Domain: conformance (58)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:stable-release-current-boundary-tier3-certification` | Stable release current-boundary Tier 3 certification | `implemented` | `active` | T3 |  | 3 | 1 |
| `feat:stable-release-rfc-security-tier3-certification` | Stable release RFC/spec/security Tier 3 certification | `implemented` | `active` | T3 |  | 3 | 1 |
| `feat:unified-tigrbl-cli-command-and-flag-surface` | Unified tigrbl CLI command and flag surface | `implemented` | `active` | T2 |  | 4 | 1 |
| `feat:supported-server-cli-smoke-dispatch` | Supported-server CLI smoke dispatch | `implemented` | `active` | T2 |  | 4 | 1 |
| `feat:evidence-registry-claim-test-artifact-map` | Evidence registry claim/test/artifact map | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:dev-bundle-evidence-structure` | Dev-bundle evidence structure | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:stable-release-evidence-structure` | Stable-release evidence structure | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:evidence-lane-ci-workflow` | Evidence-lane CI workflow | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:clean-room-package-smoke-lane` | Clean-room package smoke lane | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:evidence-registry-bundle-validator-checkpoint` | Evidence registry and bundle validator checkpoint | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:factories-001` | Canonical factories and shortcut re-exports | `implemented` | `active` | T2 | spc:2009, spc:2090 | 2 | 2 |
| `feat:gate-a-current-cycle-boundary-freeze-marker` | Gate A current-cycle boundary-freeze marker | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:gate-a-boundary-freeze-manifest` | Gate A boundary-freeze manifest exists | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:boundary-freeze-diff-enforcement` | Boundary-freeze diff enforcement exists | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:boundary-freeze-manifest-validation` | Boundary-freeze manifest validation exists | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:release-note-claim-lint` | Release-note claim lint exists | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:gate-a-checkpoint-validation-suite` | Gate A checkpoint validation suite | `implemented` | `active` | T2 | spc:2090 | 3 | 1 |
| `feat:gate-b-surface-closure-validation` | Gate B surface-closure validation | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:gate-b-surface-closure-validator-workflow` | Gate B surface-closure validator workflow | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:gate-c-conformance-security-validator-workflow` | Gate C conformance/security validator workflow | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:gate-d-reproducibility-conditions-validation` | Gate D reproducibility conditions validation | `implemented` | `active` | T2 |  | 1 | 1 |
| `feat:gate-d-reproducibility-validator-workflow` | Gate D reproducibility validator workflow | `implemented` | `active` | T2 |  | 1 | 1 |
| `feat:gate-e-release-promotion-synchronization` | Gate E release promotion synchronization | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:gate-e-promotion-validator-workflow` | Gate E promotion validator workflow | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:apache-2-license-root` | Root Apache 2.0 license | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:contributor-policy` | Contributor policy | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:code-of-conduct` | Code of conduct | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:security-policy` | Security policy | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:governed-docs-projection-tree` | Governed docs projection tree | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:package-layout-validation` | Package layout validation | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:doc-pointer-validation` | Doc-pointer validation | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:root-clutter-generated-artifact-validation` | Root-clutter and generated-artifact validation | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:claim-language-lint` | Claim-language lint | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:policy-governance-ci-workflow` | Policy governance CI workflow | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:post-promotion-release-history-freeze` | Post-promotion release history freeze | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:post-promotion-handoff-validator-workflow` | Post-promotion handoff validator workflow | `implemented` | `active` | T2 |  | 1 | 1 |
| `feat:next-dev-line-governed-opening` | Next dev line governed opening | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:next-target-datatype-table-isolation` | Next-target datatype/table isolation | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:oidc-core-discovery-descope` | OIDC Core/discovery de-scope | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:path-length-policy` | Path-length policy | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:path-length-validation` | Path-length validation | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:checkpoint-path-name-conformance` | Checkpoint path/name conformance | `implemented` | `active` | T2 |  | 3 | 1 |
| `feat:rfc-6749` | RFC-6749 feature | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:rfc-6750-http-bearer-auth-semantics` | RFC 6750 HTTP Bearer auth semantics | `implemented` | `active` | T2 |  | 5 | 1 |
| `feat:rfc-7235-http-auth-challenge-semantics` | RFC 7235 HTTP authentication challenge semantics | `implemented` | `active` | T2 |  | 5 | 1 |
| `feat:rfc-7519` | RFC-7519 feature | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:rfc-7617-http-basic-auth-semantics` | RFC 7617 HTTP Basic auth semantics | `implemented` | `active` | T2 |  | 5 | 1 |
| `feat:rfc-7636` | RFC-7636 feature | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:rfc-8414` | RFC-8414 feature | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:rfc-8705` | RFC-8705 feature | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:rfc-9110` | RFC-9110 feature | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:rfc-9449` | RFC-9449 feature | `implemented` | `active` | T2 |  | 2 | 1 |
| `feat:apikey-security-docs-runtime-alignment` | API key security docs/runtime alignment | `implemented` | `active` | T2 |  | 5 | 1 |
| `feat:http-basic-security-docs-runtime-alignment` | HTTP Basic security docs/runtime alignment | `implemented` | `active` | T2 |  | 5 | 1 |
| `feat:http-bearer-security-docs-runtime-alignment` | HTTP Bearer security docs/runtime alignment | `implemented` | `active` | T2 |  | 5 | 1 |
| `feat:oauth2-security-docs-runtime-alignment` | OAuth2 security docs/runtime alignment | `implemented` | `active` | T2 |  | 5 | 1 |
| `feat:openidconnect-security-docs-runtime-alignment` | OpenID Connect security docs/runtime alignment | `implemented` | `active` | T2 |  | 5 | 1 |
| `feat:mutualtls-security-docs-runtime-alignment` | Mutual TLS security docs/runtime alignment | `implemented` | `active` | T2 |  | 5 | 1 |

### Domain: core-governance (3)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:docs-ci-projection-validation-001` | Docs and CI projection validation | `implemented` | `active` | T2 | spc:1002, spc:2084, spc:2085 | 2 | 1 |
| `feat:ssot-authority-migration-001` | SSOT authority migration | `implemented` | `active` | T2 | spc:1002, spc:2084, spc:2085 | 2 | 1 |
| `feat:tigrbl-concrete-kernel-import-boundary-001` | tigrbl_concrete kernel import boundary | `implemented` | `active` | T2 | spc:1001, spc:2090 | 2 | 2 |

### Domain: docs-routing-core-surface (3)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:anon-access-rest-status-parity-001` | Anonymous access and REST create status parity | `implemented` | `active` | T2 | spc:2012, spc:2090 | 7 | 3 |
| `feat:auth-failure-projection-parity-001` | Authorization failure projection parity | `implemented` | `active` | T2 | spc:2012, spc:2080, spc:2090 | 7 | 3 |
| `feat:httpbearer-security-dependency-001` | HTTPBearer security dependency | `implemented` | `active` | T2 | spc:2012 | 5 | 2 |

### Domain: external-error-sanitization (1)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:external-error-detail-sanitization-001` | External persistence error detail sanitization | `implemented` | `active` | T2 | spc:2012, spc:2096, spc:2090 | 4 | 3 |

### Domain: jsonrpc-validation-hardening (2)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:jsonrpc-input-validation-before-persistence-001` | JSON-RPC input validation before persistence | `implemented` | `active` | T2 | spc:2012, spc:2014, spc:2090 | 2 | 3 |
| `feat:jsonrpc-persistence-error-sanitization-001` | JSON-RPC persistence exception response sanitization | `implemented` | `active` | T2 | spc:2012, spc:2090 | 2 | 3 |

### Domain: python-rust-fully-paritable-suite (73)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:atom-parity-dep-extra-001` | Atom parity dep extra | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-dep-param-resolver-001` | Atom parity dep param_resolver | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-dep-security-001` | Atom parity dep security | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-dispatch-binding-match-001` | Atom parity dispatch binding_match | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-dispatch-binding-parse-001` | Atom parity dispatch binding_parse | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-dispatch-input-normalize-001` | Atom parity dispatch input_normalize | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-dispatch-op-resolve-001` | Atom parity dispatch op_resolve | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-egress-asgi-send-001` | Atom parity egress asgi_send | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-egress-envelope-apply-001` | Atom parity egress envelope_apply | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-egress-headers-apply-001` | Atom parity egress headers_apply | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-egress-http-finalize-001` | Atom parity egress http_finalize | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-egress-out-dump-001` | Atom parity egress out_dump | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-egress-result-normalize-001` | Atom parity egress result_normalize | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-egress-to-transport-response-001` | Atom parity egress to_transport_response | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-emit-paired-post-001` | Atom parity emit paired_post | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-emit-paired-pre-001` | Atom parity emit paired_pre | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-emit-readtime-alias-001` | Atom parity emit readtime_alias | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-err-rollback-001` | Atom parity err rollback | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-ingress-ctx-init-001` | Atom parity ingress ctx_init | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-ingress-input-prepare-001` | Atom parity ingress input_prepare | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-ingress-transport-extract-001` | Atom parity ingress transport_extract | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-out-masking-001` | Atom parity out masking | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-refresh-demand-001` | Atom parity refresh demand | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-resolve-assemble-001` | Atom parity resolve assemble | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-resolve-paired-gen-001` | Atom parity resolve paired_gen | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-response-error-to-transport-001` | Atom parity response error_to_transport | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-response-headers-from-payload-001` | Atom parity response headers_from_payload | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-response-negotiate-001` | Atom parity response negotiate | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-response-negotiation-001` | Atom parity response negotiation | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-response-render-001` | Atom parity response render | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-response-renderer-001` | Atom parity response renderer | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-response-template-001` | Atom parity response template | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-response-templates-001` | Atom parity response templates | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-schema-collect-in-001` | Atom parity schema collect_in | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-schema-collect-out-001` | Atom parity schema collect_out | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-storage-to-stored-001` | Atom parity storage to_stored | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-commit-tx-001` | Atom parity sys commit_tx | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-db-001` | Atom parity sys db | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-aggregate-001` | Atom parity sys handler_aggregate | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-append-chunk-001` | Atom parity sys handler_append_chunk | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-bulk-create-001` | Atom parity sys handler_bulk_create | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-bulk-delete-001` | Atom parity sys handler_bulk_delete | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-bulk-merge-001` | Atom parity sys handler_bulk_merge | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-bulk-replace-001` | Atom parity sys handler_bulk_replace | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-bulk-update-001` | Atom parity sys handler_bulk_update | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-checkpoint-001` | Atom parity sys handler_checkpoint | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-clear-001` | Atom parity sys handler_clear | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-count-001` | Atom parity sys handler_count | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-create-001` | Atom parity sys handler_create | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-custom-001` | Atom parity sys handler_custom | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-delete-001` | Atom parity sys handler_delete | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-download-001` | Atom parity sys handler_download | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-exists-001` | Atom parity sys handler_exists | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-group-by-001` | Atom parity sys handler_group_by | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-list-001` | Atom parity sys handler_list | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-merge-001` | Atom parity sys handler_merge | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-noop-001` | Atom parity sys handler_noop | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-persistence-001` | Atom parity sys handler_persistence | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-publish-001` | Atom parity sys handler_publish | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-read-001` | Atom parity sys handler_read | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-replace-001` | Atom parity sys handler_replace | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-send-datagram-001` | Atom parity sys handler_send_datagram | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-subscribe-001` | Atom parity sys handler_subscribe | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-tail-001` | Atom parity sys handler_tail | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-update-001` | Atom parity sys handler_update | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-handler-upload-001` | Atom parity sys handler_upload | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-oltp-context-001` | Atom parity sys oltp_context | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-phase-db-001` | Atom parity sys phase_db | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-sys-start-tx-001` | Atom parity sys start_tx | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-wire-build-in-001` | Atom parity wire build_in | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-wire-build-out-001` | Atom parity wire build_out | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-wire-dump-001` | Atom parity wire dump | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |
| `feat:atom-parity-wire-validate-in-001` | Atom parity wire validate_in | `implemented` | `active` | T2 | spc:2090, spc:2092, spc:2093 | 5 | 5 |

### Domain: runtime-root-surface (1)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:default-root-path-contract-001` | Default root path contract | `implemented` | `active` | T2 | spc:2091 | 3 | 1 |

### Domain: server-support (4)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:server-support-gunicorn-001` | Supported server gunicorn | `implemented` | `active` | T2 | spc:2045 | 2 | 1 |
| `feat:server-support-hypercorn-001` | Supported server hypercorn | `implemented` | `active` | T2 | spc:2045 | 2 | 1 |
| `feat:server-support-tigrcorn-001` | Supported server tigrcorn | `implemented` | `active` | T2 | spc:2045 | 2 | 1 |
| `feat:server-support-uvicorn-001` | Supported server uvicorn | `implemented` | `active` | T2 | spc:2045 | 2 | 1 |

### Domain: unspecified (7)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:boundary-scoped-test-selection-001` | Boundary-scoped test selection | `implemented` | `active` | T2 | spc:2084, spc:2085 | 2 | 1 |
| `feat:feature-test-coverage-completeness-001` | Feature verification coverage completeness | `implemented` | `active` | T2 | spc:2084, spc:2085 | 2 | 1 |
| `feat:gate-evaluator-model-001` | SSOT gate evaluator model | `implemented` | `active` | T2 | spc:2084, spc:2085 | 2 | 1 |
| `feat:status-sync-engine-001` | SSOT status synchronization engine | `implemented` | `active` | T2 | spc:2084, spc:2085, spc:2090 | 3 | 2 |
| `feat:test-result-evidence-ingestion-001` | Test result evidence ingestion | `implemented` | `active` | T2 | spc:2084, spc:2085 | 2 | 1 |
| `feat:tool-test-gate-taxonomy-001` | Tool, test, evidence, and gate taxonomy | `implemented` | `active` | T2 | spc:2084, spc:2085 | 2 | 1 |
| `feat:runtime-executor-doc-endpoint-parity-001` | Runtime executor documentation endpoint parity | `partial` | `active` | T2 | spc:2077, spc:2090 | 4 | 1 |

## Priority: next (55)

### Domain: compatibility-surface (3)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:governed-module-alias-compatibility-001` | Governed module alias compatibility | `partial` | `active` | T2 | spc:2025, spc:2038, spc:2039, spc:2090 | 77 | 1 |
| `feat:orm-alias-export-compatibility-001` | tigrbl.orm alias export compatibility | `partial` | `active` | T2 | spc:2025, spc:2038, spc:2090 | 77 | 1 |
| `feat:orm-mixins-alias-compatibility-001` | tigrbl.orm.mixins alias compatibility | `partial` | `active` | T2 | spc:2038, spc:2039 | 77 | 1 |

### Domain: conformance (3)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:rfc-8785-jcs-canonicalizer-001` | RFC 8785 JCS canonicalizer | `absent` | `active` | T2 | spc:2076, spc:2090 | 2 | 1 |
| `feat:rfc-8785-jcs-conformance-vectors-001` | RFC 8785 JCS conformance vectors | `absent` | `active` | T2 | spc:2076, spc:2090 | 2 | 1 |
| `feat:rfc-8785-jcs-rejection-semantics-001` | RFC 8785 JCS rejection semantics | `absent` | `active` | T2 | spc:2076 | 1 | 0 |

### Domain: docs-routing-core-surface (6)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:canonical-datatype-catalog-semantic-center-001` | Canonical datatype catalog and semantic center | `partial` | `active` | T2 | spc:2025, spc:2090 | 3 | 2 |
| `feat:columnspec-datatype-attachment-point-001` | ColumnSpec datatype attachment point | `partial` | `active` | T2 | spc:2025, spc:2090 | 3 | 2 |
| `feat:datatype-adapter-registry-contract-001` | Datatype adapter and registry contract | `partial` | `active` | T2 | spc:2025 | 2 | 1 |
| `feat:engine-datatype-lowering-registry-bridge-001` | Engine datatype lowering and registry bridge | `partial` | `active` | T2 | spc:2025, spc:2027, spc:2090 | 3 | 2 |
| `feat:reflected-datatype-mapper-reverse-mapping-001` | Reflected datatype mapper and reverse mapping | `partial` | `active` | T2 | spc:2025 | 2 | 1 |
| `feat:schema-reflection-roundtrip-recovery-001` | Schema reflection round-trip recovery | `partial` | `active` | T2 | spc:2025 | 2 | 1 |

### Domain: extension-surface (2)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:default-canonical-engine-family-datatype-alignment-001` | Default canonical engine-family datatype alignment | `partial` | `active` | T2 | spc:2027, spc:2062, spc:2090 | 2 | 2 |
| `feat:multi-engine-table-portability-interoperability-001` | Multi-engine table portability and interoperability | `partial` | `active` | T2 | spc:2034, spc:2090 | 34 | 2 |

### Domain: op-dependency-execution (2)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:pre-tx-dependency-execution-001` | Pre-TX dependency execution | `partial` | `active` | T2 | spc:2074, spc:2044, spc:2090 | 3 | 2 |
| `feat:pre-tx-security-dependency-execution-001` | Pre-TX security dependency execution | `partial` | `active` | T2 | spc:2074, spc:2012, spc:2090 | 6 | 2 |

### Domain: ops-hooks-transport (1)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:tx-phase-legacy-alias-deprecation-001` | Deprecate legacy transaction phase aliases | `absent` | `active` | T2 | spc:2056, spc:2115 | 0 | 0 |

### Domain: runtime-parity (16)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:python-asgi-boundary-evidence-001` | Python ASGI boundary evidence | `absent` | `active` | T2 | spc:2089, spc:2088, spc:2090 | 2 | 2 |
| `feat:python-direct-runtime-microbench-001` | Python direct runtime microbenchmark lane | `absent` | `active` | T2 | spc:2088, spc:2090 | 2 | 2 |
| `feat:python-engine-session-lifecycle-001` | Python engine session lifecycle separation | `absent` | `active` | T2 | spc:2087, spc:2090 | 2 | 2 |
| `feat:python-request-envelope-contract-001` | Python request envelope contract | `absent` | `active` | T2 | spc:2089, spc:2090 | 2 | 2 |
| `feat:python-runtime-2x-target-comparison-001` | Python baseline for Rust 2x comparison | `absent` | `active` | T2 | spc:2088, spc:2090 | 2 | 2 |
| `feat:python-runtime-callgraph-export-001` | Python executor callgraph export | `absent` | `active` | T2 | spc:2088, spc:2090 | 2 | 2 |
| `feat:python-runtime-performance-baseline-001` | Python executor benchmark baseline | `absent` | `active` | T2 | spc:2088, spc:2090 | 2 | 2 |
| `feat:python-transaction-hot-path-001` | Python transaction hot path evidence | `absent` | `active` | T2 | spc:2087, spc:2088, spc:2090 | 2 | 2 |
| `feat:rust-asgi-boundary-evidence-001` | Rust executor under Python ASGI boundary evidence | `absent` | `active` | T2 | spc:2089, spc:2088, spc:2090 | 2 | 2 |
| `feat:rust-direct-runtime-microbench-001` | Rust direct runtime microbenchmark lane | `absent` | `active` | T2 | spc:2088, spc:2090 | 2 | 2 |
| `feat:rust-engine-session-lifecycle-001` | Rust engine session lifecycle separation | `absent` | `active` | T2 | spc:2087, spc:2090 | 2 | 2 |
| `feat:rust-request-envelope-contract-001` | Rust request envelope contract | `absent` | `active` | T2 | spc:2089, spc:2090 | 2 | 2 |
| `feat:rust-runtime-2x-python-target-001` | Rust executor 2x Python throughput target | `absent` | `active` | T2 | spc:2088, spc:2090 | 2 | 2 |
| `feat:rust-runtime-callgraph-export-001` | Rust executor callgraph export | `absent` | `active` | T2 | spc:2088, spc:2090 | 2 | 2 |
| `feat:rust-runtime-performance-baseline-001` | Rust executor benchmark baseline | `absent` | `active` | T2 | spc:2088, spc:2090 | 2 | 2 |
| `feat:rust-transaction-hot-path-001` | Rust transaction hot path optimization | `absent` | `active` | T2 | spc:2087, spc:2088, spc:2090 | 2 | 2 |

### Domain: spec-composition (1)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:appspec-routerspec-composition-001` | AppSpec and RouterSpec composition | `partial` | `active` | T2 | spc:1000, spc:2025 | 1 | 1 |

### Domain: surface-inventory (11)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:appspec-contract-001` | AppSpec contract | `partial` | `active` | T2 | spc:2025, spc:1000 | 1 | 1 |
| `feat:bootstrappable-table-mixin-001` | Bootstrappable table mixin | `partial` | `active` | T2 | spc:2038, spc:2039 | 77 | 1 |
| `feat:columnspec-contract-001` | ColumnSpec contract | `partial` | `active` | T2 | spc:2025, spc:1000 | 1 | 1 |
| `feat:fieldspec-contract-001` | FieldSpec contract | `partial` | `active` | T2 | spc:2025, spc:1000 | 1 | 1 |
| `feat:foreignkeyspec-contract-001` | ForeignKeySpec contract | `partial` | `active` | T2 | spc:2025, spc:1000 | 1 | 1 |
| `feat:iospec-contract-001` | IOSpec contract | `partial` | `active` | T2 | spc:2025, spc:1000 | 1 | 1 |
| `feat:opspec-contract-001` | OpSpec contract | `partial` | `active` | T2 | spc:2025, spc:2064, spc:2065, spc:2068, spc:1000 | 1 | 1 |
| `feat:responsespec-contract-001` | ResponseSpec contract | `partial` | `active` | T2 | spc:2025, spc:1000 | 1 | 1 |
| `feat:routerspec-contract-001` | RouterSpec contract | `partial` | `active` | T2 | spc:2025, spc:1000 | 1 | 1 |
| `feat:storagespec-contract-001` | StorageSpec contract | `partial` | `active` | T2 | spc:2025, spc:1000 | 1 | 1 |
| `feat:tablespec-contract-001` | TableSpec contract | `partial` | `active` | T2 | spc:2025, spc:1000 | 1 | 1 |

### Domain: transport-dispatch (4)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:executor-dispatch-removal-001` | Executors do not perform transport matching | `partial` | `active` | T2 | spc:2013, spc:2024, spc:2090 | 9 | 3 |
| `feat:kernelplan-dispatch-ownership-001` | KernelPlan and atoms own transport lookup and matching | `partial` | `active` | T2 | spc:2013, spc:2024, spc:2090 | 9 | 3 |
| `feat:transport-bypass-removal-001` | Remove non-conforming transport bypasses | `partial` | `active` | T2 | spc:2013, spc:2024, spc:2070, spc:2071, spc:2090 | 9 | 3 |
| `feat:transport-parity-contract-001` | REST and JSON-RPC parity through the shared dispatch path | `partial` | `active` | T2 | spc:2013, spc:2024, spc:2090 | 8 | 3 |

### Domain: unspecified (6)

| Feature | Title | Status | Lifecycle | Tier | Specs | Tests | Claims |
|---|---|---|---|---|---|---:|---:|
| `feat:python-request-hot-path-no-ddl-001` | Python request hot path excludes DDL | `absent` | `active` | T2 | spc:2086, spc:2088, spc:2090 | 2 | 2 |
| `feat:python-runtime-ddl-initialization-boundary-001` | Python runtime DDL initialization boundary | `absent` | `active` | T2 | spc:2086, spc:2090 | 2 | 2 |
| `feat:python-schema-readiness-fail-closed-001` | Python schema readiness fail-closed behavior | `absent` | `active` | T2 | spc:2086, spc:2090 | 2 | 2 |
| `feat:rust-request-hot-path-no-ddl-001` | Rust request hot path excludes DDL | `absent` | `active` | T2 | spc:2086, spc:2088, spc:2090 | 2 | 2 |
| `feat:rust-runtime-ddl-initialization-boundary-001` | Rust runtime DDL initialization boundary | `absent` | `active` | T2 | spc:2086, spc:2090 | 2 | 2 |
| `feat:rust-schema-readiness-fail-closed-001` | Rust schema readiness fail-closed behavior | `absent` | `active` | T2 | spc:2086, spc:2090 | 2 | 2 |

