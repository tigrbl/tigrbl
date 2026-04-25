use tigrbl_rs_kernel::KernelCompiler;
use tigrbl_rs_runtime::{RuntimeConfig, RustRuntime};
use tigrbl_rs_spec::{
    AppSpec, BindingSpec, EngineSpec, Exchange, OpKind, OpSpec, RequestEnvelope, TxScope, Value,
};

const DEFAULT_ROOT_ALIAS: &str = "__tigrbl_default_root__";

#[test]
fn runtime_instantiates_handles_from_compiled_plans() {
    let mut app = AppSpec {
        name: "demo".to_string(),
        ..AppSpec::default()
    };
    app.bindings.push(BindingSpec {
        alias: "read_user".to_string(),
        transport: "rest".to_string(),
        op: OpSpec {
            kind: OpKind::Read,
            name: "read".to_string(),
            route: Some("/users/{id}".to_string()),
            exchange: Exchange::RequestResponse,
            tx_scope: TxScope::ReadOnly,
            subevents: vec![],
        },
        ..BindingSpec::default()
    });

    let plan = KernelCompiler.compile(&app);
    let runtime = RustRuntime::new(RuntimeConfig {
        service_name: "demo-service".to_string(),
        enable_tracing: true,
        enable_metrics: true,
    });
    let handle = runtime.instantiate(plan.clone());

    assert_eq!(handle.plan, plan);
    assert!(handle.description.contains("runtime handle"));
    assert!(handle.description.contains("demo"));

    let response = handle
        .execute_rest(RequestEnvelope {
            operation: "read_user".to_string(),
            transport: "rest".to_string(),
            path: "/users/{id}".to_string(),
            method: "GET".to_string(),
            ..RequestEnvelope::default()
        })
        .unwrap_err();
    assert!(response.to_string().contains("row not found"));
}

#[test]
fn runtime_executes_crud_against_inmemory_engine() {
    let mut app = AppSpec {
        name: "demo".to_string(),
        ..AppSpec::default()
    };
    app.bindings.push(BindingSpec {
        alias: "users.create".to_string(),
        transport: "rest".to_string(),
        path: Some("/users".to_string()),
        op: OpSpec {
            kind: OpKind::Create,
            name: "create".to_string(),
            route: Some("/users".to_string()),
            exchange: Exchange::RequestResponse,
            tx_scope: TxScope::ReadWrite,
            subevents: vec![],
        },
        table: Some(tigrbl_rs_spec::TableSpec {
            name: "users".to_string(),
            columns: vec![],
        }),
        ..BindingSpec::default()
    });
    app.bindings.push(BindingSpec {
        alias: "users.read".to_string(),
        transport: "rest".to_string(),
        path: Some("/users/{id}".to_string()),
        op: OpSpec {
            kind: OpKind::Read,
            name: "read".to_string(),
            route: Some("/users/{id}".to_string()),
            exchange: Exchange::RequestResponse,
            tx_scope: TxScope::ReadOnly,
            subevents: vec![],
        },
        table: Some(tigrbl_rs_spec::TableSpec {
            name: "users".to_string(),
            columns: vec![],
        }),
        ..BindingSpec::default()
    });

    let plan = KernelCompiler.compile(&app);
    let runtime = RustRuntime::new(RuntimeConfig::default());
    let handle = runtime.instantiate(plan);

    let create = handle
        .execute_rest(RequestEnvelope {
            operation: "users.create".to_string(),
            transport: "rest".to_string(),
            path: "/users".to_string(),
            method: "POST".to_string(),
            body: Value::Object(
                [
                    ("id".to_string(), Value::String("u1".to_string())),
                    ("name".to_string(), Value::String("Ada".to_string())),
                ]
                .into_iter()
                .collect(),
            ),
            ..RequestEnvelope::default()
        })
        .unwrap();
    assert_eq!(create.status, 201);

    let read = handle
        .execute_rest(RequestEnvelope {
            operation: "users.read".to_string(),
            transport: "rest".to_string(),
            path: "/users/{id}".to_string(),
            method: "GET".to_string(),
            path_params: [("id".to_string(), Value::String("u1".to_string()))]
                .into_iter()
                .collect(),
            ..RequestEnvelope::default()
        })
        .unwrap();
    assert_eq!(read.status, 200);
    assert_eq!(
        read.body,
        Value::Object(
            [
                ("id".to_string(), Value::String("u1".to_string())),
                ("name".to_string(), Value::String("Ada".to_string())),
            ]
            .into_iter()
            .collect(),
        )
    );
}

#[test]
fn runtime_returns_default_root_without_bindings() {
    let app = AppSpec {
        name: "demo".to_string(),
        ..AppSpec::default()
    };
    let plan = KernelCompiler.compile(&app);
    let root_binding = plan
        .bindings
        .iter()
        .find(|binding| binding.alias == DEFAULT_ROOT_ALIAS)
        .expect("expected canonical default root binding")
        .clone();
    let root_route = plan
        .routes
        .iter()
        .find(|route| route.binding_alias == DEFAULT_ROOT_ALIAS)
        .expect("expected canonical default root route")
        .clone();
    let runtime = RustRuntime::new(RuntimeConfig::default());
    let handle = runtime.instantiate(plan);

    assert_eq!(root_binding.transport, "rest");
    assert_eq!(root_binding.path, "/");
    assert_eq!(root_binding.method, "GET");
    assert_eq!(root_binding.op_name, DEFAULT_ROOT_ALIAS);
    assert_eq!(root_binding.op_kind, OpKind::Read);
    assert_eq!(root_binding.table, DEFAULT_ROOT_ALIAS);
    assert_eq!(root_route.path, "/");
    assert_eq!(root_route.method, "GET");

    let response = handle
        .execute_rest(RequestEnvelope {
            transport: "rest".to_string(),
            path: "/".to_string(),
            method: "GET".to_string(),
            ..RequestEnvelope::default()
        })
        .unwrap();

    assert_eq!(response.status, 200);
    assert_eq!(
        response.body,
        Value::Object(
            [("ok".to_string(), Value::Bool(true))]
                .into_iter()
                .collect(),
        )
    );
}

#[test]
fn runtime_prefers_explicit_root_binding_over_default_root() {
    let mut app = AppSpec {
        name: "demo".to_string(),
        ..AppSpec::default()
    };
    app.bindings.push(BindingSpec {
        alias: "root.list".to_string(),
        transport: "rest".to_string(),
        path: Some("/".to_string()),
        op: OpSpec {
            kind: OpKind::List,
            name: "list".to_string(),
            route: Some("/".to_string()),
            exchange: Exchange::RequestResponse,
            tx_scope: TxScope::ReadOnly,
            subevents: vec![],
        },
        table: Some(tigrbl_rs_spec::TableSpec {
            name: "root".to_string(),
            columns: vec![],
        }),
        ..BindingSpec::default()
    });

    let plan = KernelCompiler.compile(&app);
    assert!(!plan
        .bindings
        .iter()
        .any(|binding| binding.alias == DEFAULT_ROOT_ALIAS));
    let runtime = RustRuntime::new(RuntimeConfig::default());
    let handle = runtime.instantiate(plan);

    let response = handle
        .execute_rest(RequestEnvelope {
            transport: "rest".to_string(),
            path: "/".to_string(),
            method: "GET".to_string(),
            ..RequestEnvelope::default()
        })
        .unwrap();

    assert_eq!(response.status, 200);
    assert_eq!(response.body, Value::Array(vec![]));
}

#[test]
fn runtime_rejects_python_engine_without_callback() {
    let mut app = AppSpec {
        name: "demo".to_string(),
        ..AppSpec::default()
    };
    app.engines.push(EngineSpec {
        name: "legacy".to_string(),
        kind: "sqlite".to_string(),
        language: "python".to_string(),
        callback: None,
        options: Default::default(),
    });
    app.bindings.push(BindingSpec {
        alias: "users.create".to_string(),
        transport: "rest".to_string(),
        path: Some("/users".to_string()),
        op: OpSpec {
            kind: OpKind::Create,
            name: "create".to_string(),
            route: Some("/users".to_string()),
            exchange: Exchange::RequestResponse,
            tx_scope: TxScope::ReadWrite,
            subevents: vec![],
        },
        table: Some(tigrbl_rs_spec::TableSpec {
            name: "users".to_string(),
            columns: vec![],
        }),
        ..BindingSpec::default()
    });

    let plan = KernelCompiler.compile(&app);
    let runtime = RustRuntime::new(RuntimeConfig::default());
    let handle = runtime.instantiate(plan);

    let err = handle
        .execute_rest(RequestEnvelope {
            operation: "users.create".to_string(),
            transport: "rest".to_string(),
            path: "/users".to_string(),
            method: "POST".to_string(),
            body: Value::Object(
                [("id".to_string(), Value::String("u1".to_string()))]
                    .into_iter()
                    .collect(),
            ),
            ..RequestEnvelope::default()
        })
        .unwrap_err();

    assert!(err
        .to_string()
        .contains("python-backed engine missing callback"));
}

#[test]
fn runtime_resolves_jsonrpc_bindings_by_method_name_before_shared_path() {
    let mut app = AppSpec {
        name: "demo".to_string(),
        ..AppSpec::default()
    };
    app.bindings.push(BindingSpec {
        alias: "users.create".to_string(),
        transport: "jsonrpc".to_string(),
        path: Some("/rpc".to_string()),
        op: OpSpec {
            kind: OpKind::Create,
            name: "create".to_string(),
            route: Some("/rpc".to_string()),
            exchange: Exchange::RequestResponse,
            tx_scope: TxScope::ReadWrite,
            subevents: vec![],
        },
        table: Some(tigrbl_rs_spec::TableSpec {
            name: "users".to_string(),
            columns: vec![],
        }),
        ..BindingSpec::default()
    });
    app.bindings.push(BindingSpec {
        alias: "users.read".to_string(),
        transport: "jsonrpc".to_string(),
        path: Some("/rpc".to_string()),
        op: OpSpec {
            kind: OpKind::Read,
            name: "read".to_string(),
            route: Some("/rpc".to_string()),
            exchange: Exchange::RequestResponse,
            tx_scope: TxScope::ReadOnly,
            subevents: vec![],
        },
        table: Some(tigrbl_rs_spec::TableSpec {
            name: "users".to_string(),
            columns: vec![],
        }),
        ..BindingSpec::default()
    });

    let plan = KernelCompiler.compile(&app);
    let runtime = RustRuntime::new(RuntimeConfig::default());
    let handle = runtime.instantiate(plan);

    let create = handle
        .execute_jsonrpc(RequestEnvelope {
            operation: "users.create".to_string(),
            transport: "jsonrpc".to_string(),
            path: "/rpc".to_string(),
            method: "POST".to_string(),
            body: Value::Object(
                [
                    ("id".to_string(), Value::String("u2".to_string())),
                    ("name".to_string(), Value::String("Bob".to_string())),
                ]
                .into_iter()
                .collect(),
            ),
            ..RequestEnvelope::default()
        })
        .unwrap();
    assert_eq!(create.status, 201);

    let read = handle
        .execute_jsonrpc(RequestEnvelope {
            operation: "users.read".to_string(),
            transport: "jsonrpc".to_string(),
            path: "/rpc".to_string(),
            method: "POST".to_string(),
            path_params: [("id".to_string(), Value::String("u2".to_string()))]
                .into_iter()
                .collect(),
            ..RequestEnvelope::default()
        })
        .unwrap();
    assert_eq!(read.status, 200);
    assert_eq!(
        read.body,
        Value::Object(
            [
                ("id".to_string(), Value::String("u2".to_string())),
                ("name".to_string(), Value::String("Bob".to_string())),
            ]
            .into_iter()
            .collect(),
        )
    );
}
