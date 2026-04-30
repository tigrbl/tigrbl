# Whole-Repo Certification Gap Report

This report is generated from `.ssot/registry.json` and defines the fail-closed gap set for `rel:tigrbl-0.4.0`.

## Summary

- `total_features`: `609`
- `in_bound_features`: `581`
- `out_of_scope_features`: `28`
- `feature_gap_count`: `327`
- `gap_counts`: `{'feature_not_implemented': 324, 'missing_claims': 102, 'missing_evidence': 6, 'missing_tests': 6, 'non_passing_claims': 106, 'non_passing_evidence': 73, 'non_passing_tests': 129}`
- `implementation_counts`: `{'absent': 68, 'implemented': 257, 'partial': 256}`
- `horizon_counts`: `{'backlog': 161, 'current': 291, 'future': 102, 'next': 27, 'out_of_bounds': 28}`
- `release_blocking_issue_count`: `1`
- `release_blocking_risk_count`: `1`

## Release Blockers

| Type | ID | Status | Title |
|---|---|---|---|
| issue | `iss:tigrbl-xfail-closure-implementation-blocked-001` | `open` | Tigrbl xfail closure implementation blocked |
| risk | `rsk:tigrbl-xfail-closure-overclaim-001` | `active` | Tigrbl xfail closure overclaim risk |

## Feature Gaps

| Feature | Status | Horizon | Gaps |
|---|---|---|---|
| `feat:aliasbase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:aliasspec-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:analytical-family-membership-freeze-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:analytical-runtime-docs-export-parity-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:anon-access-projection-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:api-level-auth-include-router-compat-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:apikey-security-dependency-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:app-framed-message-codec-runtime-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:app-spec-normalization-validation-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:appbase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:appbase-public-projection-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:appspec-harness-uvicorn-e2e-parity-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims`, `non_passing_tests` |
| `feat:appspec-imperative-plan-parity-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims`, `non_passing_tests` |
| `feat:asgi-router-compatibility-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:asyncapi-mount-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:asyncapi-payload-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:asyncapi-uix-surface-001` | `absent` | `backlog` | `feature_not_implemented` |
| `feat:attrdict-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:backgroundtask-concrete-class-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:bind-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:binding-driven-ingress-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims` |
| `feat:binding-subevent-phase-atom-legality-matrix-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:bindingbase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:bindingregistrybase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:bindingregistryspec-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:bindings-integration-contract-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:bindingspec-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:bindingspec-event-subevent-schema-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:bootstrap-dbschema-runtime-surface-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:bootstrappable-table-mixin-001` | `partial` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:build-asyncapi-spec-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:build-handlers-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:build-healthz-endpoint-helper-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:build-hooks-helper-surface-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:build-hookz-endpoint-helper-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:build-json-schema-bundle-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:build-kernelz-endpoint-helper-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:build-lens-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:build-methodz-endpoint-helper-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:build-openapi-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:build-openrpc-spec-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:build-rest-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:build-schemas-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:build-swagger-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:canonical-analytical-ops-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:canonical-exchange-normalization-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:canonical-ingress-route-phase-cleanup-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:canonical-op-aggregate-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-append-chunk-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-bulk-create-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-bulk-delete-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-bulk-merge-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-bulk-replace-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-bulk-update-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-checkpoint-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-clear-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-count-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-create-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-custom-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-delete-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-download-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-exists-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-group-by-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-list-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-merge-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-publish-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-read-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-replace-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-send-datagram-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-subscribe-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-tail-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-update-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-op-upload-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:canonical-realtime-transfer-ops-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:cli-module-target-resolution-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:cli-path-target-resolution-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:cli-shared-target-loader-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:cli-target-error-classification-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:cli-target-resolution-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:cli-target-surface-loading-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:columnbase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:completion-fence-emit-complete-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:core-access-compatibility-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:datatypespec-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:ddl-initialization-modes-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims`, `non_passing_tests` |
| `feat:ddl-runtime-surface-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:default-canonical-engine-catalog-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:default-kernel-identity-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:defaultsession-concrete-session-class-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims`, `non_passing_tests` |
| `feat:depends-concrete-dependency-helper-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:deprecated-export-compat-window-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:derived-runtime-subevent-taxonomy-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:diagnostics-absence-warning-suppression-001` | `partial` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:diagnostics-contract-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:diagnostics-router-mount-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:diagnostics-system-prefix-mount-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:diagnostics-warning-vocabulary-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:dispatch-exchange-family-subevent-atoms-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:docs-mount-runtime-surface-parity-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:engine-extension-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:engine-resolver-multi-table-rpc-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:engine-resolver-precedence-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:engine-session-runtime-surface-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:engine-surface-contract-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:engine-surface-plugin-resolution-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:engine-surface-public-projection-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:enginebase-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:enginedatatypebridge-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:engineproviderbase-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:engineproviderspec-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:engineregistry-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:enginespec-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:enginetypelowerer-protocol-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:ensure-primed-idempotence-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:ensure-schemas-runtime-surface-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:error-envelope-structure-parity-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:error-parity-response-structure-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:eventful-channel-state-metadata-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:eventful-protocol-decorator-surface-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:eventkey-bit-coded-dispatch-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:eventkey-hook-bucket-compilation-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:eventstreamresponse-concrete-sse-class-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:executor-dispatch-removal-001` | `partial` | `next` | `feature_not_implemented`, `non_passing_claims` |
| `feat:extended-hook-selector-matching-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:fileresponse-concrete-response-class-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:foreignkeybase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:foreignkeybase-public-projection-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:framing-decode-encode-atoms-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:gate-c-conformance-security-checkpoint-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:get-schema-python-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:harness-runtime-routing-parity-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:healthz-mount-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:healthz-stable-payload-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:healthz-uix-surface-001` | `absent` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:hook-extension-surface-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:hook-surface-attachment-ordering-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:hook-surface-phase-selector-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:hook-surface-public-projection-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:hookbase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:hookbase-public-projection-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:hookphase-vocabulary-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:hookspec-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:hookz-mount-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:hookz-payload-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:htmlresponse-concrete-response-class-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:http-jsonrpc-bindingspec-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:http-rest-bindingspec-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:http-stream-bindingspec-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:httpbasic-security-dependency-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:include-tables-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:integration-test-registry-coverage-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:json-schema-mount-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:json-schema-payload-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:json-schema-uix-surface-001` | `absent` | `backlog` | `feature_not_implemented` |
| `feat:jsonresponse-concrete-response-class-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:jsonrpc-20-runtime-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:jsonrpc-batch-framing-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:jsonrpc-endpoint-key-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:jsonrpc-notification-204-projection-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:kernel-bootstrap-plan-parity-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:kernel-cache-invalidation-contract-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:kernel-prime-opview-cache-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:kernel-priming-runtime-parity-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:kernelplan-dispatch-ownership-001` | `partial` | `next` | `feature_not_implemented`, `non_passing_claims` |
| `feat:kernelz-bounded-payload-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:kernelz-mount-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:kernelz-uix-surface-001` | `absent` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:key-digest-uvicorn-stability-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:mapping-dispatch-convergence-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:message-datagram-runtime-families-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:methodz-mount-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:methodz-payload-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:middleware-extension-surface-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:middleware-surface-auth-separation-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:middleware-surface-builtin-catalog-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:middleware-surface-protocol-composition-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:middleware-surface-public-projection-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:middlewarespec-protocol-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:monotone-spec-merge-precedence-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims` |
| `feat:mount-lens-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:mount-static-helper-surface-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:mount-swagger-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:mounted-prefix-routing-parity-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:multi-engine-interop-runtime-surface-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:multi-engine-table-portability-interoperability-001` | `implemented` | `current` | `non_passing_tests` |
| `feat:multi-table-routing-parity-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:multipart-form-preservation-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:mutualtls-security-dependency-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:oas-005` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:oauth2-security-dependency-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:op-ctx-app-owner-scope-materialization-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:op-ctx-router-owner-scope-materialization-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:op-ctx-table-owner-scope-materialization-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:op-extension-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:op-surface-custom-op-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:op-surface-default-oltp-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:op-surface-public-projection-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:opbase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:opchannel-capability-handshake-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:openapi-31-document-emission-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:openapi-components-schemas-emission-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:openapi-json-schema-dialect-2020-12-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:openapi-mount-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:openapi-mounted-json-and-docs-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:openapi-payload-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:openapi-request-response-parameter-emission-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:openapi-uix-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:openidconnect-security-dependency-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:openrpc-126-json-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:openrpc-lens-ui-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:openrpc-mount-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:openrpc-payload-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:openrpc-uix-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:operation-diagnostics-projection-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:operator-auth-dependency-hook-surface-001` | `partial` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:operator-bounded-middleware-catalog-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:operator-cookie-roundtrip-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:operator-static-files-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:operator-surface-framing-semantics-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:operator-surface-smoke-runtime-parity-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:opview-on-demand-cache-reuse-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:owner-dispatch-loop-modes-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:phase-tree-error-branches-001` | `absent` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:plaintextresponse-concrete-response-class-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:post-emit-completion-fence-compilation-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:pre-tx-dependency-execution-001` | `partial` | `next` | `feature_not_implemented` |
| `feat:primary-secondary-subevent-selection-001` | `absent` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:protocol-anchor-ordering-parity-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:protocol-fused-segments-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:protocol-phase-tree-plans-001` | `implemented` | `current` | `non_passing_claims`, `non_passing_evidence` |
| `feat:protocol-runtime-boundary-certification-001` | `absent` | `future` | `feature_not_implemented`, `missing_claims`, `missing_tests`, `missing_evidence` |
| `feat:protocol-runtime-profile-pack-001` | `absent` | `future` | `feature_not_implemented`, `missing_claims`, `missing_tests`, `missing_evidence` |
| `feat:protocol-runtime-ssot-feature-granularity-001` | `absent` | `future` | `feature_not_implemented`, `missing_claims`, `missing_tests`, `missing_evidence` |
| `feat:protocol-runtime-test-evidence-suite-001` | `absent` | `future` | `feature_not_implemented`, `missing_claims`, `missing_tests`, `missing_evidence` |
| `feat:protocol-scope-schemas-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:python-asgi-boundary-evidence-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:python-direct-runtime-microbench-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:python-engine-session-lifecycle-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:python-request-envelope-contract-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:python-request-hot-path-no-ddl-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:python-runtime-2x-target-comparison-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:python-runtime-callgraph-export-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:python-runtime-ddl-initialization-boundary-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:python-runtime-performance-baseline-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:python-schema-readiness-fail-closed-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:python-transaction-hot-path-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:realtime-transfer-family-membership-freeze-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:realtime-transfer-runtime-docs-export-parity-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:rebind-helper-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:redirectresponse-concrete-response-class-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:reflecteddatatype-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:reflectedtypemapper-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:requestbase-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:response-concrete-response-class-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:rest-create-success-status-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:rest-operation-id-uniqueness-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:rest-rpc-symmetry-header-parity-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:routerbase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:routerbase-public-projection-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:runtime-owned-hook-legality-enforcement-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:rust-asgi-boundary-evidence-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:rust-direct-runtime-microbench-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:rust-engine-session-lifecycle-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:rust-protocol-plan-parity-001` | `absent` | `future` | `feature_not_implemented`, `missing_claims`, `missing_tests`, `missing_evidence` |
| `feat:rust-request-envelope-contract-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:rust-request-hot-path-no-ddl-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:rust-runtime-2x-python-target-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:rust-runtime-callgraph-export-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:rust-runtime-ddl-initialization-boundary-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:rust-runtime-performance-baseline-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:rust-schema-readiness-fail-closed-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:rust-transaction-hot-path-001` | `absent` | `next` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:schema-migration-runtime-surface-001` | `absent` | `backlog` | `feature_not_implemented` |
| `feat:schemabase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:security-concrete-dependency-helper-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:security-per-route-include-router-compat-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:segment-fusion-barrier-policy-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:sessionabc-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:sqlite-attach-runtime-surface-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:sse-event-framing-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:sse-lazy-iterator-runtime-001` | `absent` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:static-files-surface-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:stdapi-asgi-wsgi-transport-compat-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:stdapi-openapi-docs-parity-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:stdapi-routing-parity-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:storagetransformbase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:stream-chunk-order-preservation-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:streamingresponse-concrete-stream-class-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:subevent-handler-dispatch-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:subevent-transaction-units-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:surface-binding-family-emission-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:surface-binding-proto-emission-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:surface-docs-cross-projection-parity-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:surface-metadata-omission-contract-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:surface-optional-metadata-emission-001` | `partial` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:swagger-openapi-uix-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:tablebase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:tablebase-public-projection-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:tableregistrybase-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:tableregistrybase-public-projection-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:tigrbl-lens-openrpc-uix-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:tigrbl-test-suite-coverage-intake-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests` |
| `feat:tigrblapp-concrete-facade-class-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims`, `non_passing_tests` |
| `feat:tigrblrouter-concrete-facade-class-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims`, `non_passing_tests` |
| `feat:tigrblsessionbase-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:transport-accept-emit-close-atoms-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:transport-bypass-removal-001` | `partial` | `next` | `feature_not_implemented`, `non_passing_claims` |
| `feat:transport-dispatch-governance-001` | `partial` | `backlog` | `feature_not_implemented`, `non_passing_claims` |
| `feat:transport-event-registry-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:transportresponse-concrete-response-class-001` | `absent` | `future` | `feature_not_implemented`, `missing_claims` |
| `feat:two-axis-lifecycle-matrix-001` | `implemented` | `current` | `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:tx-phase-legacy-alias-deprecation-001` | `absent` | `next` | `feature_not_implemented`, `missing_claims`, `missing_tests`, `missing_evidence` |
| `feat:tx-phase-legacy-alias-removal-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:typeadapter-protocol-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:typeregistry-contract-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:uniform-diagnostics-uix-surface-001` | `absent` | `backlog` | `feature_not_implemented` |
| `feat:uploaded-file-runtime-contract-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:uvicorn-protocol-mode-runtime-parity-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:uvicorn-rest-rpc-semantic-parity-001` | `partial` | `future` | `feature_not_implemented`, `non_passing_tests` |
| `feat:validation-failure-projection-parity-001` | `partial` | `future` | `feature_not_implemented` |
| `feat:websocket-concrete-runtime-class-001` | `partial` | `backlog` | `feature_not_implemented` |
| `feat:webtransport-transport-events-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
| `feat:well-known-concrete-constants-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:well-known-decorator-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:well-known-imperative-surface-001` | `partial` | `backlog` | `feature_not_implemented`, `missing_claims` |
| `feat:wrap-sessionmaker-helper-surface-001` | `partial` | `future` | `feature_not_implemented`, `missing_claims`, `non_passing_tests` |
| `feat:yield-iterator-producer-001` | `absent` | `current` | `feature_not_implemented`, `non_passing_claims`, `non_passing_tests`, `non_passing_evidence` |
