use tigrbl_rs_kernel::KernelCompiler;
use tigrbl_rs_runtime::{NativeRuntime, RuntimeConfig};
use tigrbl_rs_spec::{AppSpec, BindingSpec, Exchange, OpKind, OpSpec, TxScope};

#[test]
fn runtime_instantiates_handles_from_compiled_plans() {
    let mut app = AppSpec {
        name: "demo".to_string(),
        ..AppSpec::default()
    };
    app.bindings.push(BindingSpec {
        alias: "read_user".to_string(),
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
}
