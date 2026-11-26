# ASGI scope dispatch verification plan

These tests will verify SPEC-1148. The paths below identify the intended executable tests.

## ASGI scope discriminator reader boundary

`tst:asgi-scope-reader-boundary` · `pkgs/97_tests/tigrbl_tests/tests/architecture/test_asgi_scope_reader_boundary.py`

Detect raw discriminator reads outside the designated projector across production Tigrbl dispatch packages. Cover subscript, get, common aliases, and mapping patterns. Permit ASGI message type reads and report violations with file and line.

## Kernel selection from projected ASGI scope

`tst:kernel-asgi-scope-plan-selection` · `pkgs/97_tests/tigrbl_tests/tests/unit/runtime/test_kernel_asgi_scope_plan_selection.py`

Give the real kernel selector typed scope and compiled inputs. Verify plan selection for HTTP, WebSocket, WebTransport, and lifespan and verify the kernel-defined miss outcome.

## Runtime execution of kernel-selected ASGI plans

`tst:runtime-asgi-scope-plan-execution` · `pkgs/97_tests/tigrbl_tests/tests/unit/runtime/test_runtime_asgi_scope_plan_execution.py`

Verify both packed and fallback executors honor the kernel selection and miss outcome. Verify tracing, completion, and JSON-RPC batch re-entry reuse the original scope projection.

## Public ASGI app dispatch delegation

`tst:asgi-scope-dispatch-delegation` · `pkgs/97_tests/tigrbl_tests/tests/i9n/test_asgi_scope_dispatch_delegation.py`

Call TigrblApp with a guarded scope and instrument the real runtime entry, projector, and selector. Assert one raw discriminator read and one initial path selection, including batch re-entry. Verify HTTP output, WebSocket and WebTransport session events, and lifespan notifications.

## Existing tests to extend

- `tst:protocol-scope-schemas-contract` covers typed scope projection and invalid discriminators.
- `tst:tigrbl-concrete-runtime-kernel-boundary-contract` covers package imports, metadata, and runtime-mediated kernel access.

Validate the architecture check by temporarily adding a raw discriminator read in runtime. Validate the app integration check by temporarily bypassing the kernel selector. Confirm each change fails its corresponding test.
