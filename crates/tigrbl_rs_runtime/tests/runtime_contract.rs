use tigrbl_rs_kernel::KernelCompiler;
use tigrbl_rs_runtime::{NativeRuntime, RuntimeConfig};
use tigrbl_rs_spec::{AppSpec, BindingSpec, Exchange, OpKind, OpSpec, RequestEnvelope, TxScope, Value};

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
    let runtime = NativeRuntime::new(RuntimeConfig {
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
    let runtime = NativeRuntime::new(RuntimeConfig::default());
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
