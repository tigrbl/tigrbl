# Webhook and Callback Authoring Verification

Status: planned. This document specifies the future executable coverage for ADR-1210 and SPEC-1138, SPEC-1139, SPEC-1141, SPEC-2210, and SPEC-2211.

| Verification | Intended pytest file under `pkgs/97_tests/tigrbl_tests/tests/` |
|---|---|
| Public specs, serialization, concrete exports and context decorators | `unit/runtime/test_webhook_callback_public_authoring.py` |
| Equivalent callback hooks, kernel plans and invalid declarations | `unit/runtime/test_callback_authoring_plan.py` |
| Mounted webhook registration, signature checks, duplicates and acknowledgement | `i9n/test_mounted_webhook_authoring.py` |
| Signed outbound callback, original reply and transport fence ordering | `i9n/test_callback_delivery_timing.py` |
| Delivery and attempt trace linkage, redaction and persistence failures | `i9n/test_callback_trace_correlation.py` |
| Durability modes, rollback, outcome transactions and application storage mappings | `i9n/test_callback_attempt_persistence.py` |
| Concurrent claims, retry scheduling, timeouts, crash recovery and exhaustion | `i9n/test_callback_attempt_retry_recovery.py` |

Each registry test describes its expected assertions. Once executable tests exist, point the records at those files and attach execution evidence. Planned procedures do not establish runtime conformance.
