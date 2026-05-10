use tigrbl_rs_kernel::opt::hot_paths;
use tigrbl_rs_kernel::plan::models::PlanRoute;
use tigrbl_rs_kernel::KernelCompiler;
use tigrbl_rs_spec::Value;
use tigrbl_rs_spec::{AppSpec, BindingSpec, Exchange, OpKind, OpSpec, TxScope};

#[test]
fn compiler_preserves_binding_aliases_and_packs_counts() {
    let mut app = AppSpec {
        name: "demo".to_string(),
        ..AppSpec::default()
    };
    app.bindings.push(BindingSpec {
        alias: "create_user".to_string(),
        op: OpSpec {
            kind: OpKind::Create,
            name: "create".to_string(),
            route: Some("/users".to_string()),
            exchange: Exchange::RequestResponse,
            tx_scope: TxScope::ReadWrite,
            subevents: vec![],
        },
        ..BindingSpec::default()
    });
    app.bindings.push(BindingSpec {
        alias: "bulk_create_users".to_string(),
        op: OpSpec {
            kind: OpKind::BulkCreate,
            name: "bulk_create".to_string(),
            route: Some("/users/bulk".to_string()),
            exchange: Exchange::RequestResponse,
            tx_scope: TxScope::ReadWrite,
            subevents: vec![],
        },
        ..BindingSpec::default()
    });

    let plan = KernelCompiler.compile(&app);
    assert_eq!(plan.app_name, "demo");
    assert_eq!(plan.bindings.len(), 3);
    assert_eq!(plan.bindings[0].alias, "create_user");
    assert_eq!(plan.bindings[2].alias, "__tigrbl_default_root__");
    let packed = plan.packed.expect("packed plan");
    assert_eq!(packed.segments, 3);
    assert_eq!(packed.fused_steps, 3);
    assert_eq!(packed.hot_paths, 1);
}

#[test]
fn hot_path_optimizer_sorts_route_metadata_and_records_layout() {
    let mut plan = tigrbl_rs_kernel::plan::models::KernelPlan::default();
    plan.routes.push(PlanRoute {
        transport: "websocket".to_string(),
        family: "socket".to_string(),
        path: "/z".to_string(),
        method: "GET".to_string(),
        binding_alias: "z".to_string(),
        ..PlanRoute::default()
    });
    plan.routes.push(PlanRoute {
        transport: "http".to_string(),
        family: "request".to_string(),
        path: "/a".to_string(),
        method: "GET".to_string(),
        binding_alias: "a".to_string(),
        ..PlanRoute::default()
    });

    let optimized = hot_paths::apply(plan);

    assert_eq!(optimized.routes[0].binding_alias, "a");
    assert_eq!(optimized.routes[1].binding_alias, "z");
    let Value::Object(metadata) = optimized.metadata else {
        panic!("metadata should be object");
    };
    assert_eq!(
        metadata.get("layout"),
        Some(&Value::String("tiered-soa-hot-metadata".to_string()))
    );
    assert_eq!(metadata.get("routes"), Some(&Value::Integer(2)));
}
