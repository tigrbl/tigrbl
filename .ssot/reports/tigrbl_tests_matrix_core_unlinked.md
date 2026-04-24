# Core Unlinked Tests - Core Unlinked Tests

- Source: `reports/tigrbl_tests_matrix.csv`
- Rows: 259
- Same column semantics as the combined matrix.

| test_file | marker | domain | function | adr | spec | feature | feature_linked | concern_precedence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tests/harness_e2e/test_00_appspec_uvicorn_rest_rpc.py | acceptance,asyncio | acceptance-e2e | appspec uvicorn rest rpc | candidate:ADR-1016; candidate:ADR-1031; candidate:ADR-1048 | candidate:SPEC-2011; candidate:SPEC-2018 | none | no | 2 |
| tests/harness_e2e/test_01_imperative_uvicorn_rest_rpc.py | acceptance,asyncio | acceptance-e2e | imperative uvicorn rest rpc | candidate:ADR-1016; candidate:ADR-1031; candidate:ADR-1048 | candidate:SPEC-2011; candidate:SPEC-2018 | none | no | 2 |
| tests/harness/test_00_appspec_contract.py | acceptance | acceptance-harness | appspec contract | candidate:ADR-1016; candidate:ADR-1031; candidate:ADR-1048 | candidate:SPEC-2011; candidate:SPEC-2018 | none | no | 2 |
| tests/harness/test_01_kernel_plan_compilation.py | acceptance | acceptance-harness | kernel plan compilation | candidate:ADR-1016; candidate:ADR-1031; candidate:ADR-1048; candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2011; candidate:SPEC-2018; candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/harness/test_02_bootstrap_plan.py | acceptance | acceptance-harness | bootstrap plan | candidate:ADR-1016; candidate:ADR-1031; candidate:ADR-1048 | candidate:SPEC-2011; candidate:SPEC-2018 | none | no | 2 |
| tests/harness/test_03_appspec_uvicorn_e2e.py | acceptance,asyncio | acceptance-harness | appspec uvicorn e2e | candidate:ADR-1016; candidate:ADR-1031; candidate:ADR-1048 | candidate:SPEC-2011; candidate:SPEC-2018 | none | no | 2 |
| tests/architecture/test_operation_resolution_parity.py | asyncio | architecture | operation resolution parity | none | none | none | no | 2 |
| tests/architecture/test_import_graph_audit.py | none | architecture | import graph audit | none | none | none | no | 2 |
| tests/architecture/test_no_bindings_imports.py | none | architecture | no bindings imports | none | none | none | no | 2 |
| tests/architecture/test_runtime_structure.py | none | architecture | runtime structure | none | none | none | no | 2 |
| tests/architecture/test_trace_plan_parity.py | none | architecture | trace plan parity | none | none | none | no | 2 |
| tests/harness_v3/test_uvicorn_e2e_appspec.py | asyncio | harness-v3 | uvicorn e2e appspec | candidate:ADR-1016; candidate:ADR-1031; candidate:ADR-1048 | candidate:SPEC-2011; candidate:SPEC-2018 | none | no | 2 |
| tests/harness_v3/test_appspec_prefixes.py | none | harness-v3 | appspec prefixes | candidate:ADR-1016; candidate:ADR-1031; candidate:ADR-1048 | candidate:SPEC-2011; candidate:SPEC-2018 | none | no | 2 |
| tests/harness_v3/test_bootstrap_kernel_compilation.py | none | harness-v3 | bootstrap kernel compilation | candidate:ADR-1016; candidate:ADR-1031; candidate:ADR-1048 | candidate:SPEC-2011; candidate:SPEC-2018 | none | no | 2 |
| tests/harness_v3/test_kernel_plan_routing.py | skip | harness-v3 | kernel plan routing | candidate:ADR-1016; candidate:ADR-1031; candidate:ADR-1048; candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2011; candidate:SPEC-2018; candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/hooks/test_hook_ctx_phase_validation.py | none | hooks | hook ctx phase validation | candidate:ADR-1010 | candidate:SPEC-2028; candidate:SPEC-2048 | none | no | 2 |
| tests/i9n/test_bulk_docs_client.py | asyncio | integration | bulk docs client | none | none | none | no | 2 |
| tests/i9n/test_core_access.py | asyncio | integration | core access | none | none | none | no | 2 |
| tests/i9n/test_openapi_clear_response_schema.py | asyncio | integration | openapi clear response schema | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/i9n/test_sqlite_attachments.py | asyncio | integration | sqlite attachments | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/i9n/test_uvicorn_transport_behavior.py | asyncio | integration | uvicorn transport behavior | none | none | none | no | 2 |
| tests/i9n/test_v3_bulk_rest_endpoints.py | asyncio,skip | integration | v3 bulk rest endpoints | none | none | none | no | 2 |
| tests/i9n/test_acronym_route_name.py | i9n | integration | acronym route name | none | none | none | no | 2 |
| tests/i9n/test_owner_tenant_policy.py | i9n | integration | owner tenant policy | none | none | none | no | 2 |
| tests/i9n/test_types_deprecation_exports.py | i9n | integration | types deprecation exports | none | none | none | no | 2 |
| tests/i9n/test_verb_alias_policy.py | i9n | integration | verb alias policy | none | none | none | no | 2 |
| tests/i9n/test_apikey_generation.py | i9n,asyncio | integration | apikey generation | none | none | none | no | 2 |
| tests/i9n/test_bindings_modules.py | i9n,asyncio | integration | bindings modules | none | none | none | no | 2 |
| tests/i9n/test_engine_install_uvicorn.py | i9n,asyncio | integration | engine install uvicorn | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/i9n/test_engine_resolver_uvicorn.py | i9n,asyncio | integration | engine resolver uvicorn | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/i9n/test_error_mappings.py | i9n,asyncio | integration | error mappings | none | none | none | no | 2 |
| tests/i9n/test_field_spec_effects.py | i9n,asyncio | integration | field spec effects | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/i9n/test_header_io_uvicorn.py | i9n,asyncio | integration | header io uvicorn | none | none | none | no | 2 |
| tests/i9n/test_healthz_methodz_hookz.py | i9n,asyncio | integration | healthz methodz hookz | candidate:ADR-1010 | candidate:SPEC-2028; candidate:SPEC-2048 | none | no | 2 |
| tests/i9n/test_hook_ctx_v3_i9n.py | i9n,asyncio | integration | hook ctx v3 i9n | candidate:ADR-1010 | candidate:SPEC-2028; candidate:SPEC-2048 | none | no | 2 |
| tests/i9n/test_hook_lifecycle.py | i9n,asyncio | integration | hook lifecycle | candidate:ADR-1010 | candidate:SPEC-2028; candidate:SPEC-2048 | none | no | 2 |
| tests/i9n/test_iospec_attributes.py | i9n,asyncio | integration | iospec attributes | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/i9n/test_iospec_integration.py | i9n,asyncio | integration | iospec integration | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/i9n/test_key_digest_uvicorn.py | i9n,asyncio | integration | key digest uvicorn | none | none | none | no | 2 |
| tests/i9n/test_list_filters_optional.py | i9n,asyncio | integration | list filters optional | none | none | none | no | 2 |
| tests/i9n/test_mountable_favicon_uvicorn.py | i9n,asyncio | integration | mountable favicon uvicorn | candidate:ADR-1057 | candidate:SPEC-2040 | none | no | 2 |
| tests/i9n/test_nested_path_schema_and_rpc.py | i9n,asyncio | integration | nested path schema and rpc | none | none | none | no | 2 |
| tests/i9n/test_nested_routing_depth.py | i9n,asyncio | integration | nested routing depth | none | none | none | no | 2 |
| tests/i9n/test_openapi_schema_examples_presence.py | i9n,asyncio | integration | openapi schema examples presence | none | none | none | no | 2 |
| tests/i9n/test_request_extras.py | i9n,asyncio | integration | request extras | none | none | none | no | 2 |
| tests/i9n/test_rest_fallback_serialization.py | i9n,asyncio | integration | rest fallback serialization | none | none | none | no | 2 |
| tests/i9n/test_rest_row_serialization.py | i9n,asyncio | integration | rest row serialization | none | none | none | no | 2 |
| tests/i9n/test_rest_rpc_parity_v3.py | i9n,asyncio | integration | rest rpc parity v3 | none | none | none | no | 2 |
| tests/i9n/test_row_result_serialization.py | i9n,asyncio | integration | row result serialization | none | none | none | no | 2 |
| tests/i9n/test_schema.py | i9n,asyncio | integration | schema | none | none | none | no | 2 |
| tests/i9n/test_schema_ctx_attributes_integration.py | i9n,asyncio | integration | schema ctx attributes integration | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/i9n/test_schema_ctx_spec_integration.py | i9n,asyncio | integration | schema ctx spec integration | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/i9n/test_storage_spec_integration.py | i9n,asyncio | integration | storage spec integration | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/i9n/test_symmetry_parity.py | i9n,asyncio | integration | symmetry parity | none | none | none | no | 2 |
| tests/i9n/test_tigrbl_api_app_usage_uvicorn.py | i9n,asyncio | integration | tigrbl api app usage uvicorn | none | none | none | no | 2 |
| tests/i9n/test_tigrbl_api_usage_uvicorn.py | i9n,asyncio | integration | tigrbl api usage uvicorn | none | none | none | no | 2 |
| tests/i9n/test_tigrbl_api_uvicorn.py | i9n,asyncio | integration | tigrbl api uvicorn | none | none | none | no | 2 |
| tests/i9n/test_tigrbl_app_include_api_uvicorn.py | i9n,asyncio | integration | tigrbl app include api uvicorn | none | none | none | no | 2 |
| tests/i9n/test_tigrbl_app_multi_api_uvicorn.py | i9n,asyncio | integration | tigrbl app multi api uvicorn | none | none | none | no | 2 |
| tests/i9n/test_tigrbl_app_usage_uvicorn.py | i9n,asyncio | integration | tigrbl app usage uvicorn | none | none | none | no | 2 |
| tests/i9n/test_tigrbl_app_uvicorn.py | i9n,asyncio | integration | tigrbl app uvicorn | none | none | none | no | 2 |
| tests/i9n/test_v3_default_rest_ops.py | i9n,asyncio | integration | v3 default rest ops | none | none | none | no | 2 |
| tests/i9n/test_v3_default_rpc_ops.py | i9n,asyncio | integration | v3 default rpc ops | none | none | none | no | 2 |
| tests/i9n/test_mixins.py | i9n,asyncio,skip | integration | mixins | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/i9n/test_allow_anon.py | none | integration | allow anon | none | none | none | no | 2 |
| tests/i9n/test_authn_provider_integration.py | none | integration | authn provider integration | none | none | none | no | 2 |
| tests/i9n/test_bindings_integration.py | none | integration | bindings integration | none | none | none | no | 2 |
| tests/mount/test_mount_favico.py | asyncio | mount | mount favico | none | none | none | no | 2 |
| tests/parity/test_hook_runtime_phase_parity.py | none | parity | hook runtime phase parity | candidate:ADR-1010 | candidate:SPEC-2028; candidate:SPEC-2048 | none | no | 2 |
| tests/parity/test_stdapi_primitives.py | none | parity | stdapi primitives | none | none | none | no | 2 |
| tests/parity/test_stdapi_openapi_docs.py | xfail | parity | stdapi openapi docs | none | none | none | no | 2 |
| tests/parity/test_stdapi_routing.py | xfail | parity | stdapi routing | none | none | none | no | 2 |
| tests/request/test_request_response_conveniences.py | asyncio | request | request response conveniences | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/request/test_request_transport_convenience_dot_notation.py | asyncio | request | request transport convenience dot notation | none | none | none | no | 2 |
| tests/request/test_request_asgi_scope_compat.py | none | request | request asgi scope compat | none | none | none | no | 2 |
| tests/request/test_request_authn_strip.py | none | request | request authn strip | none | none | none | no | 2 |
| tests/request/test_request_dot_notation.py | none | request | request dot notation | none | none | none | no | 2 |
| tests/requests/test_request_json_modes.py | asyncio | requests | request json modes | none | none | none | no | 2 |
| tests/response/test_response_dot_notation.py | none | response | response dot notation | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/response/test_response_transport_convenience_dot_notation.py | none | response | response transport convenience dot notation | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/rust/atoms/test_rust_atoms_public_surface.py | none | rust | atoms / rust atoms public surface | none | none | none | no | 2 |
| tests/rust/ffi/test_rust_binding_trace.py | none | rust | ffi / rust binding trace | none | none | none | no | 2 |
| tests/rust/kernel/test_rust_kernel_public_surface.py | none | rust | kernel / rust kernel public surface | none | none | none | no | 2 |
| tests/rust/parity/test_rust_parity_contract.py | none | rust | parity / rust parity contract | none | none | none | no | 2 |
| tests/rust/runtime/test_rust_runtime_engine_policy.py | none | rust | runtime / rust runtime engine policy | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/rust/runtime/test_rust_runtime_public_surface.py | none | rust | runtime / rust runtime public surface | none | none | none | no | 2 |
| tests/security/test_dot_notation_schemes.py | none | security | dot notation schemes | none | none | none | no | 2 |
| tests/unit/runtime/test_kernel_plan_full_ordering.py | asyncio | unit | runtime / kernel plan full ordering | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/test_base_facade_initialize.py | asyncio | unit | base facade initialize | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064; candidate:ADR-1059; candidate:ADR-1061 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050; candidate:SPEC-2042; candidate:SPEC-2044; candidate:SPEC-2047 | none | no | 2 |
| tests/unit/test_column_rest_rpc_results.py | asyncio | unit | column rest rpc results | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_engine_spec_and_shortcuts.py | asyncio | unit | engine spec and shortcuts | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_hookz_empty_phase.py | asyncio | unit | hookz empty phase | candidate:ADR-1010 | candidate:SPEC-2028; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/test_hybrid_session_run_sync.py | asyncio | unit | hybrid session run sync | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_initialize_async_task.py | asyncio | unit | initialize async task | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_initialize_cross_ddl.py | asyncio | unit | initialize cross ddl | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_initialize_mixed_engines.py | asyncio | unit | initialize mixed engines | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_initialize_task_schedule.py | asyncio | unit | initialize task schedule | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_kernel_invoke_ctx.py | asyncio | unit | kernel invoke ctx | none | none | none | no | 2 |
| tests/unit/test_kernelz_endpoint.py | asyncio | unit | kernelz endpoint | none | none | none | no | 2 |
| tests/unit/test_middleware_http_and_cors.py | asyncio | unit | middleware http and cors | candidate:ADR-1054 | candidate:SPEC-2030 | none | no | 2 |
| tests/unit/test_postgres_engine_errors.py | asyncio | unit | postgres engine errors | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_response_alias_table_rpc.py | asyncio | unit | response alias table rpc | candidate:ADR-1018; candidate:ADR-1056; candidate:ADR-1058 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039; candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_response_diagnostics_kernelz.py | asyncio | unit | response diagnostics kernelz | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_response_html_jinja_behavior.py | asyncio | unit | response html jinja behavior | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_response_parity.py | asyncio | unit | response parity | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_response_rpc.py | asyncio | unit | response rpc | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_response_template.py | asyncio | unit | response template | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_rest_no_schema_jsonable.py | asyncio | unit | rest no schema jsonable | none | none | none | no | 2 |
| tests/unit/test_rpc_all_default_op_verbs.py | asyncio | unit | rpc all default op verbs | none | none | none | no | 2 |
| tests/unit/test_sqlite_attachments.py | asyncio | unit | sqlite attachments | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_stdapi_request_injection.py | asyncio | unit | stdapi request injection | none | none | none | no | 2 |
| tests/unit/test_sys_tx_async_begin.py | asyncio | unit | sys tx async begin | none | none | none | no | 2 |
| tests/unit/test_sys_tx_begin.py | asyncio | unit | sys tx begin | none | none | none | no | 2 |
| tests/unit/test_sys_tx_commit.py | asyncio | unit | sys tx commit | none | none | none | no | 2 |
| tests/unit/test_v3_favicon_endpoint.py | asyncio | unit | v3 favicon endpoint | candidate:ADR-1057 | candidate:SPEC-2040 | none | no | 2 |
| tests/unit/test_v3_healthz_endpoint.py | asyncio | unit | v3 healthz endpoint | none | none | none | no | 2 |
| tests/unit/test_in_tx.py | asyncio,skip | unit | in tx | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_stdapi_transport_asgi_wsgi.py | asyncio,xfail | unit | stdapi transport asgi wsgi | none | none | none | no | 2 |
| tests/unit/decorators/test_alias_ctx_bindings.py | none | unit | decorators / alias ctx bindings | none | none | none | no | 2 |
| tests/unit/decorators/test_engine_ctx_bindings.py | none | unit | decorators / engine ctx bindings | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/decorators/test_hook_ctx_bindings.py | none | unit | decorators / hook ctx bindings | candidate:ADR-1010 | candidate:SPEC-2028; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/decorators/test_response_ctx_bindings.py | none | unit | decorators / response ctx bindings | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/decorators/test_schema_ctx_bindings.py | none | unit | decorators / schema ctx bindings | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/runtime/atoms/test_emit_paired_post.py | none | unit | runtime / atoms / emit paired post | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_emit_paired_pre.py | none | unit | runtime / atoms / emit paired pre | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_emit_readtime_alias.py | none | unit | runtime / atoms / emit readtime alias | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_out_masking.py | none | unit | runtime / atoms / out masking | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_refresh_demand.py | none | unit | runtime / atoms / refresh demand | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_resolve_assemble.py | none | unit | runtime / atoms / resolve assemble | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_resolve_paired_gen.py | none | unit | runtime / atoms / resolve paired gen | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_route_protocol_detect.py | none | unit | runtime / atoms / route protocol detect | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_schema_collect_in.py | none | unit | runtime / atoms / schema collect in | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_schema_collect_out.py | none | unit | runtime / atoms / schema collect out | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_storage_to_stored.py | none | unit | runtime / atoms / storage to stored | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_wire_build_in.py | none | unit | runtime / atoms / wire build in | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_wire_build_out.py | none | unit | runtime / atoms / wire build out | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_wire_dump.py | none | unit | runtime / atoms / wire dump | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/atoms/test_wire_validate_in.py | none | unit | runtime / atoms / wire validate in | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/test_atom_stage_phase_window_static.py | none | unit | runtime / atom stage phase window static | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/test_compilation_runtime_behavior.py | none | unit | runtime / compilation runtime behavior | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/test_events_phases.py | none | unit | runtime / events phases | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/test_events_runtime_behavior.py | none | unit | runtime / events runtime behavior | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/test_ingress_egress_phase_access.py | none | unit | runtime / ingress egress phase access | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/test_kernel_plan_event_ordering.py | none | unit | runtime / kernel plan event ordering | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/test_kernel_runtime_behavior.py | none | unit | runtime / kernel runtime behavior | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/test_ordering_runtime_behavior.py | none | unit | runtime / ordering runtime behavior | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/runtime/test_payload_select_header_merge.py | none | unit | runtime / payload select header merge | none | none | none | no | 2 |
| tests/unit/runtime/test_payload_select_invalid_rpc_params.py | none | unit | runtime / payload select invalid rpc params | none | none | none | no | 2 |
| tests/unit/test_acol_vcol_knobs.py | none | unit | acol vcol knobs | none | none | none | no | 2 |
| tests/unit/test_alias_ctx_op_attributes.py | none | unit | alias ctx op attributes | none | none | none | no | 2 |
| tests/unit/test_app_model_defaults.py | none | unit | app model defaults | none | none | none | no | 2 |
| tests/unit/test_app_reexport.py | none | unit | app reexport | none | none | none | no | 2 |
| tests/unit/test_attrdict_vs_simplenamespace.py | none | unit | attrdict vs simplenamespace | none | none | none | no | 2 |
| tests/unit/test_base_columnspec_inheritance.py | none | unit | base columnspec inheritance | none | none | none | no | 2 |
| tests/unit/test_build_list_params_spec_model.py | none | unit | build list params spec model | none | none | none | no | 2 |
| tests/unit/test_bulk_body_annotation.py | none | unit | bulk body annotation | none | none | none | no | 2 |
| tests/unit/test_bulk_response_schema.py | none | unit | bulk response schema | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_colspec_map_isolation.py | none | unit | colspec map isolation | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_column_collect_mixins.py | none | unit | column collect mixins | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_column_mro_collect_namespace.py | none | unit | column mro collect namespace | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_column_table_orm_binding.py | none | unit | column table orm binding | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_config_dataclass_none.py | none | unit | config dataclass none | none | none | none | no | 2 |
| tests/unit/test_db_dependency.py | none | unit | db dependency | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_decorator_and_collect.py | none | unit | decorator and collect | none | none | none | no | 2 |
| tests/unit/test_default_schema_selection.py | none | unit | default schema selection | none | none | none | no | 2 |
| tests/unit/test_default_tags.py | none | unit | default tags | none | none | none | no | 2 |
| tests/unit/test_diagnostics_no_compat_module.py | none | unit | diagnostics no compat module | none | none | none | no | 2 |
| tests/unit/test_engine_session_database_availability.py | none | unit | engine session database availability | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_engine_usage_levels.py | none | unit | engine usage levels | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_field_spec_attrs.py | none | unit | field spec attrs | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_file_response.py | none | unit | file response | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_get_schema.py | none | unit | get schema | none | none | none | no | 2 |
| tests/unit/test_handler_step_qualname.py | none | unit | handler step qualname | none | none | none | no | 2 |
| tests/unit/test_hook_ctx_attributes.py | none | unit | hook ctx attributes | candidate:ADR-1010 | candidate:SPEC-2028; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/test_hook_ctx_binding.py | none | unit | hook ctx binding | candidate:ADR-1010 | candidate:SPEC-2028; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/test_include_model_columns_namespace.py | none | unit | include model columns namespace | none | none | none | no | 2 |
| tests/unit/test_include_models_base_prefix.py | none | unit | include models base prefix | none | none | none | no | 2 |
| tests/unit/test_include_tables_base_prefix.py | none | unit | include tables base prefix | none | none | none | no | 2 |
| tests/unit/test_instance_naming_conventions.py | none | unit | instance naming conventions | none | none | none | no | 2 |
| tests/unit/test_io_spec_attributes.py | none | unit | io spec attributes | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_iospec_attributes.py | none | unit | iospec attributes | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_iospec_effects.py | none | unit | iospec effects | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_jsonrpc_id_example.py | none | unit | jsonrpc id example | none | none | none | no | 2 |
| tests/unit/test_jsonrpc_router_default_tag.py | none | unit | jsonrpc router default tag | none | none | none | no | 2 |
| tests/unit/test_kernel_opview_on_demand.py | none | unit | kernel opview on demand | none | none | none | no | 2 |
| tests/unit/test_kernel_plan_labels.py | none | unit | kernel plan labels | candidate:ADR-1008; candidate:ADR-1009; candidate:ADR-1023; candidate:ADR-1024 | candidate:SPEC-2046; candidate:SPEC-2047; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/test_make_column_shortcuts.py | none | unit | make column shortcuts | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_mapping_bind_response_export.py | none | unit | mapping bind response export | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_mapping_plan_precedence.py | none | unit | mapping plan precedence | none | none | none | no | 2 |
| tests/unit/test_mixins_sqlalchemy.py | none | unit | mixins sqlalchemy | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_op_class_engine_binding.py | none | unit | op class engine binding | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_openapi_openrpc_schema_separation.py | none | unit | openapi openrpc schema separation | none | none | none | no | 2 |
| tests/unit/test_phase1_declared_surface_docs.py | none | unit | phase1 declared surface docs | none | none | none | no | 2 |
| tests/unit/test_postgres_env_vars.py | none | unit | postgres env vars | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_relationship_alias_cols.py | none | unit | relationship alias cols | none | none | none | no | 2 |
| tests/unit/test_request_body_schema.py | none | unit | request body schema | none | none | none | no | 2 |
| tests/unit/test_request_response_examples.py | none | unit | request response examples | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_resolver_interning_warmup.py | none | unit | resolver interning warmup | none | none | none | no | 2 |
| tests/unit/test_resolver_precedence.py | none | unit | resolver precedence | none | none | none | no | 2 |
| tests/unit/test_response_ctx_precedence.py | none | unit | response ctx precedence | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_response_rest.py | none | unit | response rest | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_response_uuid.py | none | unit | response uuid | candidate:ADR-1058 | candidate:SPEC-2041 | none | no | 2 |
| tests/unit/test_rest_bulk_delete_suppresses_clear.py | none | unit | rest bulk delete suppresses clear | none | none | none | no | 2 |
| tests/unit/test_rest_output_serialization_extras.py | none | unit | rest output serialization extras | none | none | none | no | 2 |
| tests/unit/test_rest_request_mapping_access.py | none | unit | rest request mapping access | none | none | none | no | 2 |
| tests/unit/test_rest_rpc_prefixes.py | none | unit | rest rpc prefixes | none | none | none | no | 2 |
| tests/unit/test_schema_ctx_attributes.py | none | unit | schema ctx attributes | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_schema_ctx_plain_class.py | none | unit | schema ctx plain class | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_schema_spec_presence.py | none | unit | schema spec presence | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_schemas_binding.py | none | unit | schemas binding | none | none | none | no | 2 |
| tests/unit/test_should_wire_canonical.py | none | unit | should wire canonical | none | none | none | no | 2 |
| tests/unit/test_spec_api.py | none | unit | spec api | none | none | none | no | 2 |
| tests/unit/test_spec_app.py | none | unit | spec app | none | none | none | no | 2 |
| tests/unit/test_spec_column.py | none | unit | spec column | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_spec_engine.py | none | unit | spec engine | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_spec_field.py | none | unit | spec field | none | none | none | no | 2 |
| tests/unit/test_spec_hook.py | none | unit | spec hook | candidate:ADR-1010 | candidate:SPEC-2028; candidate:SPEC-2048 | none | no | 2 |
| tests/unit/test_spec_io.py | none | unit | spec io | none | none | none | no | 2 |
| tests/unit/test_spec_op.py | none | unit | spec op | none | none | none | no | 2 |
| tests/unit/test_spec_storage.py | none | unit | spec storage | none | none | none | no | 2 |
| tests/unit/test_spec_table.py | none | unit | spec table | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_sqlite_uuid_type.py | none | unit | sqlite uuid type | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_storage_spec_attributes.py | none | unit | storage spec attributes | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_sys_handler_crud.py | none | unit | sys handler crud | none | none | none | no | 2 |
| tests/unit/test_sys_run_rollback.py | none | unit | sys run rollback | none | none | none | no | 2 |
| tests/unit/test_table_base_exports.py | none | unit | table base exports | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_table_collect_spec.py | none | unit | table collect spec | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_table_columns_namespace.py | none | unit | table columns namespace | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_table_model_attribute_contract.py | none | unit | table model attribute contract | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_table_namespace_init.py | none | unit | table namespace init | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_table_namespace_isolation.py | none | unit | table namespace isolation | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_transport_gw_contract.py | none | unit | transport gw contract | none | none | none | no | 2 |
| tests/unit/test_transport_security_runtime_only.py | none | unit | transport security runtime only | none | none | none | no | 2 |
| tests/unit/test_v3_schemas_and_decorators.py | none | unit | v3 schemas and decorators | none | none | none | no | 2 |
| tests/unit/test_v3_storage_spec_attributes.py | none | unit | v3 storage spec attributes | candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_verbosity.py | none | unit | verbosity | none | none | none | no | 2 |
| tests/unit/test_engine_install_api.py | unit | unit | engine install api | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_engine_install_app.py | unit | unit | engine install app | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_engine_install_op.py | unit | unit | engine install op | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050 | none | no | 2 |
| tests/unit/test_engine_install_table.py | unit | unit | engine install table | candidate:ADR-1012; candidate:ADR-1015; candidate:ADR-1055; candidate:ADR-1064; candidate:ADR-1018; candidate:ADR-1056 | candidate:SPEC-2032; candidate:SPEC-2033; candidate:SPEC-2034; candidate:SPEC-2035; candidate:SPEC-2036; candidate:SPEC-2037; candidate:SPEC-2048; candidate:SPEC-2050; candidate:SPEC-2031; candidate:SPEC-2038; candidate:SPEC-2039 | none | no | 2 |
| tests/unit/test_router_dependency_execution_blocked.py | unit | unit | router dependency execution blocked | none | none | none | no | 2 |
| tests/unit/test_tigrbl_api_app_configuration.py | unit | unit | tigrbl api app configuration | none | none | none | no | 2 |
| tests/unit/test_tigrbl_api_app_instantiation.py | unit | unit | tigrbl api app instantiation | none | none | none | no | 2 |
| tests/unit/test_tigrbl_api_app_subclass_definition.py | unit | unit | tigrbl api app subclass definition | none | none | none | no | 2 |
| tests/unit/test_tigrbl_api_configuration.py | unit | unit | tigrbl api configuration | none | none | none | no | 2 |
| tests/unit/test_tigrbl_api_instantiation.py | unit | unit | tigrbl api instantiation | none | none | none | no | 2 |
| tests/unit/test_tigrbl_api_subclass_definition.py | unit | unit | tigrbl api subclass definition | none | none | none | no | 2 |
| tests/unit/test_tigrbl_app_configuration.py | unit | unit | tigrbl app configuration | none | none | none | no | 2 |
| tests/unit/test_tigrbl_app_instantiation.py | unit | unit | tigrbl app instantiation | none | none | none | no | 2 |
| tests/unit/test_tigrbl_app_state.py | unit | unit | tigrbl app state | none | none | none | no | 2 |
| tests/unit/test_tigrbl_app_subclass_definition.py | unit | unit | tigrbl app subclass definition | none | none | none | no | 2 |
| tests/unit/test_tigrbl_app_event_handlers.py | unit,asyncio | unit | tigrbl app event handlers | none | none | none | no | 2 |
| tests/unit/test_router_compatibility_shims.py | unit,asyncio,xfail | unit | router compatibility shims | none | none | none | no | 2 |
| tests/unit/test_core_wrap_memoization.py | unit,perf,asyncio | unit | core wrap memoization | none | none | none | no | 2 |
| tests/unit/test_api_level_set_auth.py | xfail | unit | api level set auth | none | none | none | no | 2 |
| tests/unit/test_app_spec_normalization.py | xfail | unit | app spec normalization | none | none | none | no | 2 |
| tests/unit/test_rest_operation_id_uniqueness.py | xfail | unit | rest operation id uniqueness | none | none | none | no | 2 |
| tests/unit/test_rest_rpc_symmetry.py | xfail | unit | rest rpc symmetry | none | none | none | no | 2 |
| tests/unit/test_security_per_route.py | xfail | unit | security per route | none | none | none | no | 2 |
