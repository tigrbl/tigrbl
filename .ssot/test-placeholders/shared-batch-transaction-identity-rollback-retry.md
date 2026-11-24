# Shared batch transaction identity across rollback and retry

Planned conformance scenario.

Dispatch two invocations into one authorized batch transaction. Force the first transaction to roll back, then retry with a new engine transaction and commit. Both invocations link to each engine-issued transaction ID, keep their own correlation and invocation IDs, and get the appropriate retry attempt identity. Verify one begin and one terminal outcome per transaction, no authority for participants to commit independently, and a rollup count of two transactions despite four participation links.

## Executable targets

- `pkgs/97_tests/tigrbl_tests/tests/i9n/test_resident_batch_scheduler_runtime.py`
- `pkgs/40_atoms/tigrbl_atoms/tests/test_resident_batch_scheduler.py`

Use scheduler integration coverage to observe real transaction boundaries and invocation-to-transaction links. Use scheduler unit coverage for ownership and error branches. Verify counts again after exporting the batch and applying the rollup contract.
