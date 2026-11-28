# Raw ASGI handoff and compiled route-handler verification

SPEC-1148 defines the runtime-to-kernel handoff. SPEC-1155 defines compiled handler execution. Passing evidence for the earlier runtime-led handoff remains historical. The linked executable tests and pytest evidence record verification of the revised boundaries.

## Raw ASGI handoff

- `tst:runtime-raw-asgi-forwarding` targets `pkgs/050_runtime/tigrbl_runtime/tests/test_raw_asgi_forwarding.py`. Spy on the configured kernel entry point and assert one call with exactly the three original ASGI objects. Scope and carrier spies detect reads, writes, copying, wrapping, or carrier calls by runtime. Assert that the kernel outcome, original exception, and cancellation propagate through the forwarder.
- Extend `tst:asgi-scope-reader-boundary` in `pkgs/210_tests/tigrbl_tests/tests/architecture/test_asgi_scope_reader_boundary.py`. Keep the sole reader assertion for raw scope type and show that runtime cannot invoke the scope projector. ASGI message discriminators are governed separately.
- Extend `tst:kernel-asgi-scope-plan-selection` in `pkgs/210_tests/tigrbl_tests/tests/unit/runtime/test_kernel_asgi_scope_plan_selection.py`. Drive the kernel ASGI entry point. Assert that the kernel projects once before selecting HTTP, WebSocket, WebTransport, or lifespan. Cover invalid discriminators that stop before selection and applicable kernel miss outcomes.
- Extend `tst:asgi-scope-dispatch-delegation` in `pkgs/210_tests/tigrbl_tests/tests/i9n/test_asgi_scope_dispatch_delegation.py`. Enter through TigrblApp.__call__ for all four scope kinds. Observe the original objects at kernel entry and the expected carrier behavior. Cover reuse of the same projection during tracing, completion, and JSON-RPC batch re-entry. Preserve the authored WebSocket socket API and existing WebTransport session-plan coverage.

The previously executed `tst:runtime-asgi-scope-plan-execution` documents the runtime-led handoff. Its claim and evidence links retain that record. The new forwarding test provides active coverage for the revised runtime contract.

## Compiled route-handler bridge

- `tst:compiled-route-handler-plan` targets `pkgs/045_kernel/tigrbl_kernel/tests/test_compiled_route_handler_plan.py`. Assert that the compiled plan carries operation identity, the authored callable, and argument sources. Exercise an invocation with a guarded concrete route registry and signature probe so either a second alias lookup or handler signature inspection fails.
- `tst:compiled-route-handler-asgi-parity` targets `pkgs/210_tests/tigrbl_tests/tests/i9n/test_compiled_route_handler_execution.py`. Enter public ASGI for exact and templated routes through packed and fallback execution. Cover sync and async handlers, path parameters, context, and the public Request adapter. Compare operation identity, bound arguments, and observable results. Assert one handler invocation per operation.
- `tst:compiled-route-handler-dependency-lifetime` targets the same integration file. Cover configured overrides, sync and async generator dependencies, reverse teardown order, success, handler failure, cancellation, and partial acquisition failure. The public ASGI cases replace direct private bridge coverage in `pkgs/070_concrete/tigrbl_concrete/tests/test_async_generator_dependencies.py`. Reuse the three existing pre-transaction dependency tests to prove operation-level secdeps and deps retain their declared phases and short-circuit behavior.
- `tst:compiled-route-handler-egress` targets the same integration file. Cover plain, response-like, and streaming results. Verify status, headers, body or ordered chunks, one response start, and one terminal body event. Verify the first streaming chunk is observable while the producer is still open.
