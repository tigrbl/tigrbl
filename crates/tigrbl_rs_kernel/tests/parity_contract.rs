use tigrbl_rs_kernel::{build_parity_snapshot, KernelCompiler};
use tigrbl_rs_spec::{
    AppSpec, BindingSpec, Exchange, HookPhase, HookSpec, OpKind, OpSpec, TxScope,
};

#[test]
fn kernel_parity_snapshot_covers_routes_opviews_phases_packed_and_docs() {
    let mut app = AppSpec {
        name: "phase4-demo".to_string(),
        ..AppSpec::default()
    };
    app.bindings.push(BindingSpec {
        alias: "create_widget".to_string(),
        transport: "rest".to_string(),
        path: Some("/widgets".to_string()),
        op: OpSpec {
            kind: OpKind::Create,
            name: "create".to_string(),
            route: Some("/widgets".to_string()),
            exchange: Exchange::RequestResponse,
            tx_scope: TxScope::ReadWrite,
            subevents: vec![],
        },
        hooks: vec![HookSpec {
            name: "pre".to_string(),
            phase: HookPhase::PreHandler,
            ..HookSpec::default()
        }],
        ..BindingSpec::default()
    });
    app.bindings.push(BindingSpec {
        alias: "events".to_string(),
        transport: "sse".to_string(),
        path: Some("/events".to_string()),
        op: OpSpec {
            kind: OpKind::Subscribe,
            name: "subscribe".to_string(),
            route: Some("/events".to_string()),
            exchange: Exchange::ServerStream,
            tx_scope: TxScope::None,
            subevents: vec!["chunk".to_string()],
        },
        ..BindingSpec::default()
    });

    let plan = KernelCompiler.compile(&app);
    let snapshot = build_parity_snapshot(&app, &plan);

    assert_eq!(snapshot.app_name, "phase4-demo");
    assert_eq!(snapshot.routes.len(), 2);
    assert_eq!(snapshot.opviews[0].hook_count, 1);
    assert_eq!(
        snapshot.phase_plans.get("create_widget").unwrap(),
        &vec![
            "INGRESS_BEGIN",
            "INGRESS_DISPATCH",
            "START_TX",
            "PRE_HANDLER",
            "HANDLER",
            "POST_HANDLER",
            "TX_COMMIT",
            "POST_RESPONSE",
        ]
    );
    assert_eq!(
        snapshot.phase_plans.get("events").unwrap(),
        &vec![
            "INGRESS_BEGIN",
            "INGRESS_DISPATCH",
            "PRE_HANDLER",
            "HANDLER",
            "POST_HANDLER",
            "POST_EMIT",
            "POST_RESPONSE",
        ]
    );
    assert_eq!(snapshot.packed_plan.segments, 2);
    assert_eq!(snapshot.docs.openapi_paths, vec!["/widgets".to_string()]);
    assert_eq!(snapshot.docs.asyncapi_channels, vec!["/events".to_string()]);
}
